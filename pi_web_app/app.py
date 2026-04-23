from flask import Flask, render_template_string
import pygame
import threading
import time

app = Flask(__name__)

# Global variable to hold controller state
controller_state = {
    'connected': False,
    'buttons': {},
    'axes': {}
}

def read_controller():
    global controller_state
    pygame.init()
    pygame.joystick.init()

    joystick = None
    while True:
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            controller_state['connected'] = True
            break
        time.sleep(1)

    while True:
        pygame.event.pump()
        if joystick:
            # Read buttons
            buttons = {}
            for i in range(joystick.get_numbuttons()):
                buttons[f'button_{i}'] = joystick.get_button(i)
            controller_state['buttons'] = buttons

            # Read axes
            axes = {}
            for i in range(joystick.get_numaxes()):
                axes[f'axis_{i}'] = round(joystick.get_axis(i), 2)
            controller_state['axes'] = axes
        else:
            controller_state['connected'] = False
        time.sleep(0.1)

# Start controller reading in a separate thread
threading.Thread(target=read_controller, daemon=True).start()

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PS4 Controller Status</title>
        <meta http-equiv="refresh" content="1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status { margin: 10px 0; }
            .connected { color: green; }
            .disconnected { color: red; }
            .section { margin: 20px 0; }
            .item { margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>PS4 Controller Status</h1>
        <div class="status">
            <strong>Controller: </strong>
            <span class="{{ 'connected' if controller_state['connected'] else 'disconnected' }}">
                {{ 'Connected' if controller_state['connected'] else 'Disconnected' }}
            </span>
        </div>
        <div class="section">
            <h2>Buttons</h2>
            {% for btn, val in controller_state['buttons'].items() %}
            <div class="item">{{ btn }}: {{ val }}</div>
            {% endfor %}
        </div>
        <div class="section">
            <h2>Axes</h2>
            {% for ax, val in controller_state['axes'].items() %}
            <div class="item">{{ ax }}: {{ val }}</div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, controller_state=controller_state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)