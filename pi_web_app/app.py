from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import pygame
import threading
import time
import subprocess

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variable to hold controller state
controller_state = {
    'connected': False,
    'buttons': {},
    'axes': {},
    'bt_devices': [],
    'bt_status': 'Unknown'
}

# PS4 button mapping
BUTTON_NAMES = {
    0: 'Square',
    1: 'X',
    2: 'Circle',
    3: 'Triangle',
    4: 'L1',
    5: 'R1',
    6: 'L2',
    7: 'R2',
    8: 'Share',
    9: 'Options',
    10: 'L3',
    11: 'R3',
    12: 'PS',
    13: 'Touchpad'
}

AXIS_NAMES = {
    0: 'Left Stick X',
    1: 'Left Stick Y',
    2: 'Right Stick X',
    3: 'Right Stick Y',
    4: 'L2 Trigger',
    5: 'R2 Trigger'
}

BT_TARGET_NAMES = ['Wireless Controller', 'PS4 Controller']

def run_btctl(commands, timeout=10):
    try:
        result = subprocess.run(['bluetoothctl'] + commands,
                                capture_output=True, stderr=subprocess.STDOUT,
                                text=True,
                                timeout=timeout)
        return result.stdout.strip()
    except Exception:
        return ''

def parse_bt_devices(output):
    devices = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('Device '):
            parts = line.split(' ', 2)
            if len(parts) >= 3:
                devices.append({'mac': parts[1], 'name': parts[2].strip()})
    return devices

def get_bt_device_info(mac):
    info = {'connected': False, 'paired': False, 'trusted': False}
    output = run_btctl(['info', mac])
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('Connected:'):
            info['connected'] = line.split(':', 1)[1].strip() == 'yes'
        if line.startswith('Paired:'):
            info['paired'] = line.split(':', 1)[1].strip() == 'yes'
        if line.startswith('Trusted:'):
            info['trusted'] = line.split(':', 1)[1].strip() == 'yes'
    return info

def refresh_bt_devices():
    paired_output = run_btctl(['paired-devices'])
    scanned_output = run_btctl(['devices'])

    devices = parse_bt_devices(paired_output)
    scan_devices = parse_bt_devices(scanned_output)

    devices_by_mac = {device['mac']: device for device in scan_devices}
    for device in devices:
        if device['mac'] in devices_by_mac:
            devices_by_mac[device['mac']].update(device)
        else:
            devices_by_mac[device['mac']] = device

    devices = list(devices_by_mac.values())
    for device in devices:
        device.update(get_bt_device_info(device['mac']))

    controller_state['bt_devices'] = devices
    controller_state['bt_status'] = 'Ready' if devices else 'No bluetooth devices found'
    return devices

def ensure_bt_powered():
    output = run_btctl(['show'])
    for line in output.splitlines():
        if line.strip().startswith('Powered:'):
            powered = line.split(':', 1)[1].strip()
            if powered == 'no':
                run_btctl(['power', 'on'])
            return

def connect_bluetooth_device(mac):
    run_btctl(['trust', mac])
    result = run_btctl(['connect', mac])
    return 'Connection successful' in result or 'successful' in result.lower()

def auto_connect_controller():
    if controller_state['connected']:
        return
    for device in controller_state['bt_devices']:
        if device['name'] in BT_TARGET_NAMES and not device.get('connected'):
            connect_bluetooth_device(device['mac'])
            time.sleep(2)
            device.update(get_bt_device_info(device['mac']))
            break

def bluetooth_manager():
    while True:
        ensure_bt_powered()
        refresh_bt_devices()
        auto_connect_controller()
        time.sleep(15)

def read_controller():
    global controller_state
    pygame.init()
    pygame.joystick.init()
    joystick = None
    while True:
        pygame.event.pump()
        count = pygame.joystick.get_count()
        if count > 0 and joystick is None:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            controller_state['connected'] = True
        elif count == 0 and joystick is not None:
            joystick = None
            controller_state['connected'] = False
            controller_state['buttons'] = {}
            controller_state['axes'] = {}
        if joystick:
            try:
                buttons = {}
                for i in range(joystick.get_numbuttons()):
                    name = BUTTON_NAMES.get(i, f'Button {i}')
                    buttons[name] = joystick.get_button(i) == 1
                controller_state['buttons'] = buttons
                axes = {}
                for i in range(joystick.get_numaxes()):
                    name = AXIS_NAMES.get(i, f'Axis {i}')
                    axes[name] = round(joystick.get_axis(i), 2)
                controller_state['axes'] = axes
            except pygame.error:
                joystick = None
                controller_state['connected'] = False
        time.sleep(0.1)

# Start controller reading in a separate thread
threading.Thread(target=read_controller, daemon=True).start()
threading.Thread(target=bluetooth_manager, daemon=True).start()

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PS4 Controller Monitor</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .status {
                text-align: center;
                font-size: 1.2em;
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.2);
            }
            .connected { color: #4CAF50; }
            .disconnected { color: #f44336; }
            .section {
                margin: 30px 0;
                padding: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            .section h2 {
                margin-top: 0;
                border-bottom: 2px solid rgba(255, 255, 255, 0.3);
                padding-bottom: 10px;
            }
            .buttons-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .button {
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid transparent;
            }
            .button.pressed {
                background: #4CAF50;
                border-color: #45a049;
                transform: scale(0.95);
            }
            .axes-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .axis {
                padding: 15px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                text-align: center;
            }
            .axis-value {
                font-size: 1.5em;
                font-weight: bold;
                margin-top: 5px;
            }
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                overflow: hidden;
                margin-top: 10px;
            }
            .progress-fill {
                height: 100%;
                background: #2196F3;
                transition: width 0.3s ease;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 PS4 Controller Monitor</h1>
            <div class="status" id="status">
                <strong>Controller: </strong>
                <span class="disconnected">Disconnected</span>
            </div>
            <div class="section">
                <h2>Buttons</h2>
                <div class="buttons-grid" id="buttons">
                    <!-- Buttons will be populated by JavaScript -->
                </div>
            </div>
            <div class="section">
                <h2>Axes</h2>
                <div class="axes-list" id="axes">
                    <!-- Axes will be populated by JavaScript -->
                </div>
            </div>
            <div class="section">
                <h2>Bluetooth Devices</h2>
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                    <div>Status: <strong id="bt-status">Unknown</strong></div>
                    <button onclick="refreshBluetooth()" style="padding:10px 18px;border:none;border-radius:8px;background:#2196F3;color:#fff;cursor:pointer;">Refresh</button>
                </div>
                <div class="buttons-grid" id="bt-list" style="margin-top:20px;"></div>
            </div>
        </div>

        <script>
            const socket = io();
            const statusEl = document.getElementById('status').querySelector('span');
            const buttonsEl = document.getElementById('buttons');
            const axesEl = document.getElementById('axes');
            const btStatusEl = document.getElementById('bt-status');
            const btListEl = document.getElementById('bt-list');

            function renderBluetooth(devices) {
                btListEl.innerHTML = '';
                if (!devices.length) {
                    btListEl.innerHTML = '<div class="button" style="grid-column: span 2;">No paired devices found</div>';
                    return;
                }
                devices.forEach(device => {
                    const deviceEl = document.createElement('div');
                    deviceEl.className = 'button';
                    let statusText = device.connected ? 'Connected' : 'Disconnected';
                    deviceEl.innerHTML = `<strong>${device.name}</strong><br>${device.mac}<br>${statusText}`;
                    if (!device.connected) {
                        const connectBtn = document.createElement('button');
                        connectBtn.textContent = 'Connect';
                        connectBtn.style.marginTop = '10px';
                        connectBtn.style.padding = '8px 12px';
                        connectBtn.style.border = 'none';
                        connectBtn.style.borderRadius = '6px';
                        connectBtn.style.background = '#4CAF50';
                        connectBtn.style.color = '#fff';
                        connectBtn.style.cursor = 'pointer';
                        connectBtn.onclick = () => connectDevice(device.mac);
                        deviceEl.appendChild(connectBtn);
                    }
                    btListEl.appendChild(deviceEl);
                });
            }

            function connectDevice(mac) {
                fetch(`/bluetooth/connect/${encodeURIComponent(mac)}`)
                    .then(resp => resp.json())
                    .then(data => {
                        btStatusEl.textContent = data.status;
                        renderBluetooth(data.devices);
                    })
                    .catch(() => {
                        btStatusEl.textContent = 'Connection failed';
                    });
            }

            function refreshBluetooth() {
                fetch('/bluetooth/refresh')
                    .then(resp => resp.json())
                    .then(data => {
                        btStatusEl.textContent = data.status;
                        renderBluetooth(data.devices);
                    });
            }

            socket.on('update', function(data) {
                // Update status
                statusEl.textContent = data.connected ? 'Connected' : 'Disconnected';
                statusEl.className = data.connected ? 'connected' : 'disconnected';

                // Update buttons
                buttonsEl.innerHTML = '';
                Object.entries(data.buttons).forEach(([name, pressed]) => {
                    const buttonEl = document.createElement('div');
                    buttonEl.className = `button ${pressed ? 'pressed' : ''}`;
                    buttonEl.textContent = name;
                    buttonsEl.appendChild(buttonEl);
                });

                // Update axes
                axesEl.innerHTML = '';
                Object.entries(data.axes).forEach(([name, value]) => {
                    const axisEl = document.createElement('div');
                    axisEl.className = 'axis';
                    axisEl.innerHTML = `
                        <div>${name}</div>
                        <div class="axis-value">${value}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(value + 1) * 50}%"></div>
                        </div>
                    `;
                    axesEl.appendChild(axisEl);
                });

                btStatusEl.textContent = data.bt_status;
                renderBluetooth(data.bt_devices);
            });

            // Load Bluetooth list immediately
            refreshBluetooth();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/bluetooth/refresh')
def bluetooth_refresh():
    devices = refresh_bt_devices()
    return jsonify({'status': controller_state['bt_status'], 'devices': devices})

@app.route('/bluetooth/connect/<mac>')
def bluetooth_connect(mac):
    success = connect_bluetooth_device(mac)
    refresh_bt_devices()
    return jsonify({'status': 'Connected' if success else 'Failed', 'devices': controller_state['bt_devices']})

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update', controller_state)

def emit_updates():
    while True:
        socketio.emit('update', controller_state)
        time.sleep(0.1)

# Start emitting updates in a separate thread
threading.Thread(target=emit_updates, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)