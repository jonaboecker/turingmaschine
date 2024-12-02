"""
This module contains the Flask application for the TMZA project.
It defines the routes and its associated functions.
"""

import os
from flask import (Flask, request, redirect, url_for, render_template, flash, send_from_directory)

import assets

# import assets
# import hardware_control.color_sensor as cs
# import hardware_control.light_barrier as lb
# import hardware_control.stepper_motor as sm

app = Flask(__name__)

# ------------------------------------------------------------------------------------------
# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = os.environ.get('Flask_Secret_Key_WISSINGER')
app.secret_key = 'this is a very secure secret key which we will definitely replace later'
# Konfiguration für den Upload-Ordner
app.config['UPLOAD_FOLDER'] = assets.UPLOAD_FOLDER

# ------------------------------------------------------------------------------------------


@app.route('/')
def index():
    """Renders the index page."""
    programms = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', programms=programms), 200


# Funktion, um Dateiendungen zu prüfen
def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in assets.ALLOWED_EXTENSIONS


# Route für den Upload
@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the uploaded file."""
    print("upload_file")
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
        flash(f"Das Programm {file.filename} existiert bereits und wird überschrieben.")
    file.save(filepath)
    flash(f"Datei {file.filename} erfolgreich hochgeladen!", 'success')
    return redirect(url_for('index'))


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



# DOCS------------------------------------------------------------------
@app.route('/docs')
def docs():
    """Renders the documentation page."""
    return render_template('docs.html'), 200


@app.route('/docs/<doc>')
def show_doc(doc):
    """Renders the requested documentation .pdf."""
    return send_from_directory(app.static_folder, f'docs/{doc}.pdf'), 200


# PWA-------------------------------------------------------------------
@app.route('/manifest.json')
def serve_manifest():
    """Serves the manifest.json file."""
    return send_from_directory(app.static_folder, 'pwa/manifest.json'), 200


@app.route('/service-worker.js')
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
