"""
This module contains the Flask application for the TMZA project.
It defines the routes and its associated functions.
"""

import os
from pprint import pprint
from flask import (Flask, request, redirect, url_for, render_template, flash, send_from_directory)

from assets import UPLOAD_FOLDER, PROGRAM_LANGUAGES, ALLOWED_EXTENSIONS
import turingmachine_interpreter as tm_interp
import dannweisstobiesnicht as sm

# pylint: disable=global-statement
app = Flask(__name__)
MACHINE = None

# ------------------------------------------------------------------------------------------
# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = os.environ.get('Flask_Secret_Key_WISSINGER')
app.secret_key = 'this is a very secure secret key which we will definitely replace later'
# Konfiguration für den Upload-Ordner
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ------------------------------------------------------------------------------------------


@app.route('/', methods=['GET'])
def index():
    """Renders the index page."""
    programms = os.listdir(app.config['UPLOAD_FOLDER'])
    languages = [lang.value for lang in PROGRAM_LANGUAGES]
    return render_template('index.html', languages=languages,
                           programms=programms), 200


# Funktion, um Dateiendungen zu prüfen
def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# pylint: disable=too-many-return-statements
@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the uploaded file."""
    language = PROGRAM_LANGUAGES(request.form['language'])
    if not language:
        flash('Keine oder unbekannte Sprache ausgewählt', 'error')
        return redirect(request.url)
    print(language)
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt', 'error')
        return redirect(request.url)
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
    # file_path = '/mnt/data/palindrome.txt'
    tm_code = tm_interp.parse_turing_machine(filepath, language)
    pprint(tm_code)
    if tm_code["errors"]:
        return render_template('parser_error.html', errors=tm_code["errors"],
                               warnings=tm_code["warnings"], tm_code=tm_code), 200
    return render_template('parser_error.html',
                           warnings=tm_code["warnings"], tm_code=tm_code), 200


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
    """Runs the provided program."""
    global MACHINE
    program = request.form['program']
    if not program:
        flash('Kein Programm ausgewählt', 'error')
        return redirect(url_for('index'))
    language = PROGRAM_LANGUAGES(request.form['language'])
    if not language:
        flash('Keine oder unbekannte Sprache ausgewählt', 'error')
        return redirect(url_for('index'))
    print(language)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], program)
    tm_code = tm_interp.parse_turing_machine(filepath, language)
    pprint(tm_code)
    # Implement the run function here
    if tm_code["errors"]:
        return render_template('parser_error.html', errors=tm_code["errors"],
                               warnings=tm_code["warnings"], tm_code=tm_code), 200
    MACHINE = sm.StateMachine(tm_code)
    MACHINE.run()
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
        'errors': MACHINE.errors
    }
    return render_template('running_program.html', infos=infos), 200


# Route, um hochgeladene Dateien aufzulisten
# @app.route('/files')
# def uploaded_files():
#     files = os.listdir(app.config['UPLOAD_FOLDER'])
#     return render_template('files.html', files=files)
#
# # Route, um eine Datei herunterzuladen
# @app.route('/files/<filename>')
#
# def download_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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
    app.run()
