from flask import Flask,request
import psutil
import subprocess
import time

from sympy import false
from werkzeug.utils import send_file

app = Flask('__name__')
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_mem_info():
    swp= psutil.swap_memory()
    mem = psutil.virtual_memory()
    return {
        'total' : mem.total,
        'used': mem.used,
        'swp_total':swp.total,
        'swp_usage':swp.used
    }


def get_gpu_usage():
    """this may depend on your Raspberry Pi system version or model"""
    try:
        result = subprocess.check_output(['vcgencmd', 'get_mem', 'gpu'], text=True)
        gpu_mem = int(result.strip().split('=')[1].replace('M', ''))
        result = subprocess.check_output(['vcgencmd', 'measure_clock', 'v3d'], text=True)
        gpu_clock = int(result.strip().split('=')[1])
        return {
            'memory_mb': gpu_mem,
            'gpu_clock': round(gpu_clock/1e6, 2)
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'memory_mb': 0,
            'gpu_clock': 0
        }

last_disk_io = None
last_disk_io_time = None
def get_disk_io():
    """this is not the precise disk io it's roundly calculate by disk io counters"""
    global last_disk_io, last_disk_io_time

    current_disk_io = psutil.disk_io_counters()
    current_time = time.time()

    if last_disk_io is None or last_disk_io_time is None:
        last_disk_io = current_disk_io
        last_disk_io_time = current_time
        return {
            'read_bytes': 0,
            'write_bytes': 0
        }

    time_delta = current_time - last_disk_io_time
    read_bytes_delta = current_disk_io.read_bytes - last_disk_io.read_bytes
    write_bytes_delta = current_disk_io.write_bytes - last_disk_io.write_bytes

    read_bytes_per_sec = read_bytes_delta / time_delta
    write_bytes_per_sec = write_bytes_delta / time_delta

    last_disk_io = current_disk_io
    last_disk_io_time = current_time

    return {
        'read_bytes': read_bytes_per_sec,
        'write_bytes': write_bytes_per_sec
    }

last_net_io = None
last_net_io_time = None
def get_net_io():
    """this is not the precise network io, it's calculate by net io counters"""
    global last_net_io, last_net_io_time
    current_net_io = psutil.net_io_counters()
    current_time = time.time()

    if last_net_io is None or last_net_io_time is None:
        last_net_io = current_net_io
        last_net_io_time = current_time
        return {
            'bytes_sent': 0,
            'bytes_recv': 0
        }

    time_delta = current_time - last_net_io_time
    bytes_sent_delta = current_net_io.bytes_sent - last_net_io.bytes_sent
    bytes_recv_delta = current_net_io.bytes_recv - last_net_io.bytes_recv

    send_bytes_per_sec = bytes_sent_delta / time_delta
    recv_bytes_per_sec = bytes_recv_delta / time_delta

    last_net_io = current_net_io
    last_net_io_time = current_time

    return {
        'bytes_sent': send_bytes_per_sec,
        'bytes_recv': recv_bytes_per_sec
    }

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent
    }

def get_temperature():
    try:
        result = subprocess.check_output(['vcgencmd', 'measure_temp'], text=True)
        temp = float(result.strip().replace('temp=', '').replace("'C", ''))
        return temp
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0

isConnected = false
lastFetchTime = None
@app.route('/')
def index():
    global isConnected
    if lastFetchTime is None:
        isConnected = False
    elif time.time() - lastFetchTime >= 2:
        isConnected = False
    else:
        isConnected = True
    if not isConnected:
        return send_file('templates/index.html', request.environ)
    else:
        return send_file('templates/RefuseConnect.html', request.environ)

@app.route('/Data')
def send_datas():
    global lastFetchTime
    lastFetchTime = time.time()
    gpu_data = get_gpu_usage()
    mem_info = get_mem_info()
    disk_info= get_disk_io()
    net_info = get_net_io()
    disk_Usage = get_disk_usage()
    data = {
        'cpuUsage': get_cpu_usage(),
        'gpuUsage': gpu_data['gpu_clock'],
        'memTotal': round(mem_info['total']/(1024*1024*1024),1),
        'memUsage': round(mem_info['used']/(1024*1024*1024),1),
        'swpTotal': round(mem_info['swp_total']/(1024*1024*1024),1),
        'swpUsage': round(mem_info['swp_usage']/(1024*1024*1024),1),
        'gMem': gpu_data['memory_mb'],
        'diskRead': round(disk_info['read_bytes']),
        'diskWrite': round(disk_info['write_bytes']),
        'netReceive': round(net_info['bytes_recv'],0),
        'netSend': round(net_info['bytes_sent'],0),
        'temperature': get_temperature(),
        'diskTotal': disk_Usage['total'],
        'diskUsed': disk_Usage['used']
    }
    return data


app.run(host='0.0.0.0', port=5000)



