# Raspberry Pi 5 Web System Resource Monitor

## Introduction
A lightweight web-based system resource monitor designed for Raspberry Pi 5. The web interface runs on port 5000 by default. This is an early-stage project with core functionality established. Built with Flask.

**Note:** This project may not receive timely updates.

## Installation

1. **Clone or download the project:**
   ```bash
   git clone <your-repo-url>
   # Or download the ZIP file from the Code tab and extract it
   ```
   Then navigate to the project directory:
   ```bash
   cd <project-directory>
   ```

2. **Set up a virtual environment and install dependencies:**
   ```bash
   python3 -m venv .web-monitor
   source .web-monitor/bin/activate
   pip install -r requirements.txt
   ```

   *Note: Use `python3.11` specifically if you require that version, but `python3` is generally sufficient.*

3. **Run the application:**
   ```bash
   python web-monitor.py
   ```
   *Requires Python >= 3.7*

## Running as a System Service (Optional)

To run the monitor as a background service, you can set up a systemd service file.

### For all users (system-wide):
1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/web-monitor.service
   ```

2. Add the following content (adjust paths and Python version as needed):
   ```ini
   [Unit]
   Description=Web System Resource Monitor for Raspberry Pi 5
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/path/to/your/web-monitor
   ExecStart=/path/to/your/web-monitor/.web-monitor/bin/python /path/to/your/web-monitor/web-monitor.py
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable web-monitor
   sudo systemctl start web-monitor
   ```

### For current user only:
Place the service file in `~/.config/systemd/user/` and use:
```bash
systemctl --user enable web-monitor
systemctl --user start web-monitor
```

### Service management:
- **Check status:** `sudo systemctl status web-monitor`
- **Stop service:** `sudo systemctl stop web-monitor`
- **Restart service:** `sudo systemctl restart web-monitor`

## Changing the Web Port

To change the default port (5000), edit `web-monitor.py`:

Find this line:
```python
app.run(host='0.0.0.0', port=5000)
```

Change the `port` value to your desired port number, for example:
```python
app.run(host='0.0.0.0', port=8080)
```
