"""
This module contains the Flask application for the TMZA project.
It defines the routes and its associated functions.
"""

import os
import json
import ctypes
from pprint import pprint
from threading import Thread
from flask import (Flask, request, redirect, url_for, render_template, flash, send_from_directory)
from flask_socketio import SocketIO, emit

import assets
import turingmachine_interpreter as tm_interp
import dannweisstobiesnicht as sm

# pylint: disable=global-statement
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

MACHINE: sm.StateMachine | None = None
CURRENT_MACHINE_THREAD: Thread | None = None

# INIT--------------------------------------------------------------------------------------
# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = os.environ.get('ENVIRONMENT_SECRET_KEY')
app.secret_key = 'this is a very secure secret key which we will definitely replace later'


def load_config():
    """Loads and returns the config from the config.json file. Fallback to default values."""
    if os.path.exists(assets.CONFIG_PATH):
        with open(assets.CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {  # Fallback
        "LED_AMOUNT": assets.LED_AMOUNT,
        "STEPS_BETWEEN_LEDS": assets.STEPS_BETWEEN_LEDS,
        "STEPS_BETWEEN_HOME_TO_FIRST_LED": assets.STEPS_BETWEEN_HOME_TO_FIRST_LED,
        "TOGGLE_IO_BAND_RETRYS": assets.TOGGLE_IO_BAND_RETRYS,
        "UPLOAD_FOLDER": assets.UPLOAD_FOLDER
    }


app.config.update(load_config())  # Set the config values

# CONFIG------------------------------------------------------------------------------------

CONFIG_FIELDS = ["LED_AMOUNT", "STEPS_BETWEEN_LEDS", "STEPS_BETWEEN_HOME_TO_FIRST_LED",
                 "TOGGLE_IO_BAND_RETRYS", "UPLOAD_FOLDER"]

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Renders the settings page and updates config on POST request."""
    if request.method == 'GET':
        config = {key: app.config[key] for key in CONFIG_FIELDS}
        return render_template('settings.html', config=config), 200
    for key in CONFIG_FIELDS:
        if key in request.form:
            try:
                app.config[key] = type(app.config[key])( request.form[key]) # Check Type
            except ValueError:
                flash(f'Ungültiger Wert für {key}', 'error')
                return redirect(url_for('settings'))

    # save new config in config.json persistently
    with open(assets.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({key: app.config[key] for key in CONFIG_FIELDS}, f)
    flash('Einstellungen erfolgreich aktualisiert!', 'success')
    return redirect(url_for('settings'))


# WEB-SOCKET--------------------------------------------------------------------------------

@socketio.on('connect')
def handle_connect():
    """Handles the websocket connection of a new client."""
    print('Client connected')
    broadcast_machine_state()


def broadcast_machine_state():
    """Broadcasts the machine state to all connected clients every second."""
    if MACHINE:
        socketio.emit('state_update', {
            'program_name': MACHINE.program_name,
            'state': MACHINE.current_state,
            'step': MACHINE.steps,
            'position': MACHINE.position,
            'run': MACHINE.running,
            'pause': MACHINE.pause,
            'speed': MACHINE.speed,
            'errors': MACHINE.errors,
            'should_stop': MACHINE.should_stop
        })


@socketio.on('disconnect')
def handle_disconnect():
    """Handles the websocket disconnection of a client."""
    print('Client disconnected', request.sid)


@socketio.on('command')
def handle_command(data):
    """Handles incoming commands from the client."""
    if not MACHINE and not MACHINE.running:
        emit('error', {'message': 'No machine is running'})
        return

    command = data.get('command')
    if command == 'resume':
        if MACHINE.pause:
            MACHINE.resume_program()
        elif not MACHINE.running or MACHINE.should_stop:
            emit('error', {'message': 'Maschine ist nicht am Laufen'})
        else:
            emit('error', {'message': 'Maschine ist nicht pausiert'})
    elif command == 'pause':
        if MACHINE.pause:
            emit('error', {'message': 'Maschine ist bereits pausiert'})
            return
        if not MACHINE.running or MACHINE.should_stop:
            emit('error', {'message': 'Maschine ist nicht am Laufen'})
            return
        MACHINE.pause_program()
    elif command == 'stop':
        if not MACHINE.running or MACHINE.should_stop:
            emit('error', {'message': 'Maschine ist nicht am Laufen'})
            return
        MACHINE.stop_program()
    elif command == 'speed':
        speed = int(data.get('value'))
        MACHINE.change_speed(speed)
    emit('confirmation', {'message': f'Command {command} executed'})


# ------------------------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    """Renders the index page."""
    programms = os.listdir(app.config['UPLOAD_FOLDER'])
    languages = [lang.value for lang in assets.PROGRAM_LANGUAGES]
    return render_template('index.html', languages=languages,
                           programms=programms), 200


def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in assets.ALLOWED_EXTENSIONS


# pylint: disable=too-many-return-statements
@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the uploaded file."""
    language = assets.PROGRAM_LANGUAGES(request.form['language'])
    if not language:
        flash('Keine oder unbekannte Sprache ausgewählt', 'error')
        return redirect(url_for('index'))
    print(language)
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt', 'error')
        return redirect(url_for('index'))
    file = request.files['file']
    print(file)
    if not file:
        flash('Upload fehlgeschlagen', 'error')
        return redirect(url_for('index'))
    if file.filename == '':
        flash('Keine Datei ausgewählt', 'error')
        return redirect(url_for('index'))
    if not allowed_file(file.filename):
        flash('Ungültige Datei. Bitte nur .txt Dateien hochladen.', 'error')
        return redirect(url_for('index'))
    # ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    # Check if file already exists
    if os.path.exists(filepath):
        flash(f"Das Programm {file.filename} existiert bereits und wird überschrieben.", 'error')
    file.save(filepath)
    flash(f"Datei {file.filename} erfolgreich hochgeladen!", 'success')
    # analyze file
    tm_code = tm_interp.parse_turing_machine(filepath, language)
    pprint(tm_code)
    if tm_code["errors"] or tm_code["warnings"]:
        return render_template('parser_error.html', errors=tm_code["errors"],
                               warnings=tm_code["warnings"], tm_code=tm_code), 200
    return redirect(url_for('index'))


@app.route('/delete/<programm>', methods=['GET'])
def delete_file(programm):
    """Deletes the provided programm."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], programm)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f"Programm {programm} erfolgreich gelöscht!", 'success')
    else:
        flash(f"Programm {programm} nicht gefunden.", 'error')
    return redirect(url_for('index'))


@app.route('/run', methods=['POST'])
def run_program():
    """Runs the provided program. Stops current program if running."""
    global MACHINE, CURRENT_MACHINE_THREAD

    # Check if a machine is already running
    if MACHINE and MACHINE.running:
        MACHINE.stop_program()
        if CURRENT_MACHINE_THREAD:
            CURRENT_MACHINE_THREAD.join()  # Wait for the machine to come to a finish point
        else:
            assert False, "MACHINE is running but there is no CURRENT_MACHINE_THREAD"

    # Load the new program
    program = request.form['program']
    if not program:
        flash('Kein Programm ausgewählt', 'error')
        return redirect(url_for('index'))
    language = assets.PROGRAM_LANGUAGES(request.form['language'])
    if not language:
        flash('Keine oder unbekannte Sprache ausgewählt', 'error')
        return redirect(url_for('index'))
    print(language)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], program)
    tm_code = tm_interp.parse_turing_machine(filepath, language)
    print(f"Program {program} loaded with language {language}. Machine code:")
    pprint(tm_code)
    if tm_code["errors"]:
        return render_template('parser_error.html', errors=tm_code["errors"],
                               warnings=tm_code["warnings"], tm_code=tm_code), 200

    # Create and start a new machine
    MACHINE = sm.StateMachine(tm_code, app)
    MACHINE.add_listener(broadcast_machine_state)

    def background_task():
        """Runs the machine in a separate thread."""
        MACHINE.run()

    CURRENT_MACHINE_THREAD = Thread(target=background_task, daemon=True, name=f"TMZA-{program}")
    CURRENT_MACHINE_THREAD.start()

    return redirect(url_for('running_program'))


@app.route('/running_program', methods=['GET'])
def running_program():
    """Renders the running program page."""
    # global MACHINE
    if not MACHINE:
        flash('Was soll ich denn anzeigen, wenn sich noch nichts bewegt?', 'error')
        return redirect(url_for('index'))
    infos = {
        'program_name': MACHINE.program_name,
        'state': MACHINE.current_state,
        'step': MACHINE.steps,
        'run': MACHINE.running,
        'pause': MACHINE.pause,
        'speed': MACHINE.speed,
        'errors': MACHINE.errors,
        'should_stop': MACHINE.should_stop,
        'position': MACHINE.position
    }
    return render_template('running_program.html', infos=infos), 200


@app.route('/emergency_stop', methods=['GET'])
def emergency_stop():
    """emergency stops a running maschine immediately."""
    global MACHINE, CURRENT_MACHINE_THREAD

    if not MACHINE or not MACHINE.running:
        flash('Keine laufende Maschine für den Nothalt gefunden.', 'error')
        return redirect(url_for('index'))

    if not CURRENT_MACHINE_THREAD or not CURRENT_MACHINE_THREAD.is_alive():
        flash('Keinen laufenden Maschinen-Thread für den Nothalt gefunden.', 'error')
        return redirect(url_for('index'))
    ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(CURRENT_MACHINE_THREAD.ident),
        ctypes.py_object(SystemExit)
    )
    # reset the machine
    MACHINE = None
    CURRENT_MACHINE_THREAD = None
    flash('Emergency-Stop ausgeführt. Maschine gestoppt.', 'success')
    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    """Serves the requested file."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# PWA-------------------------------------------------------------------
@app.route('/manifest.json', methods=['GET'])
def serve_manifest():
    """Serves the manifest.json file."""
    return send_from_directory(app.static_folder, 'pwa/manifest.json'), 200


@app.route('/service-worker.js', methods=['GET'])
def serve_service_worker():
    """Serves the service-worker.js file."""
    return send_from_directory(app.static_folder, 'pwa/service-worker.js'), 200


# ERROR-----------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    """Renders the 404 error page."""
    # logger().warning("404 error: %s - %s", request.url, e)
    print("404 error: %s - %s", request.url, e)
    return render_template('errorHandling/404.html'), 404


@app.route('/robots.txt', methods=['GET'])
def robots():
    """Serves the robots.txt file."""
    return send_from_directory(app.static_folder, 'robots.txt'), 200


# MAIN------------------------------------------------------------------
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
