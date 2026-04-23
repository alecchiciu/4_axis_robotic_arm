# Raspberry Pi PS4 Controller Web Monitor

This project sets up a web server on your Raspberry Pi to monitor and display PS4 controller inputs in real-time.

## Setup Instructions

### 1. Update and Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip bluetooth bluez-utils
pip3 install -r requirements.txt
```

### 2. Enable Bluetooth and Pair PS4 Controller
```bash
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

To pair the PS4 controller:
- Press and hold the PlayStation button and Share button on the controller until the light bar starts flashing.
- On the Pi, run:
```bash
bluetoothctl
```
Then in bluetoothctl:
```
power on
agent on
scan on
```
Wait for the controller to appear (it should show as "Wireless Controller").
```
pair <MAC_ADDRESS>
trust <MAC_ADDRESS>
connect <MAC_ADDRESS>
quit
```

### 3. Run the Web App
```bash
python3 app.py
```

The app will run on port 5000. Access it from your laptop at `http://<PI_IP>:5000`

### 4. Run as Background Service (Recommended)
To run the app automatically on startup:

1. Copy the service file:
```bash
sudo cp ps4-monitor.service /etc/systemd/system/
```

2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ps4-monitor
sudo systemctl start ps4-monitor
```

3. Check status:
```bash
sudo systemctl status ps4-monitor
```

4. View logs:
```bash
sudo journalctl -u ps4-monitor -f
```

To stop the service:
```bash
sudo systemctl stop ps4-monitor
sudo systemctl disable ps4-monitor
```

### 4. Connecting Pi to Laptop for Uploading
- Enable SSH on Pi: `sudo raspi-config` -> Interfacing Options -> SSH -> Enable
- Find Pi's IP: `hostname -I`
- From laptop (Windows), use PuTTY or VS Code Remote SSH extension to connect.
- For file transfer, use SCP or SFTP.

## Notes
- The web page refreshes every second to show current controller state.
- If controller disconnects, it will show as disconnected.
- For the robotic arm control, you can extend this to send commands based on inputs.