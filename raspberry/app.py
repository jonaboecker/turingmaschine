"""
This module contains the Flask application for the TMZA project.
It defines the routes and its associated functions.
"""

from flask import (Flask, render_template, send_from_directory, request)

# import assets
# import hardware_control.color_sensor as cs
# import hardware_control.light_barrier as lb
# import hardware_control.stepper_motor as sm

app = Flask(__name__)

# ------------------------------------------------------------------------------------------
# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = os.environ.get('Flask_Secret_Key_WISSINGER')
app.secret_key = 'this is a very secure secret key which we will definitely replace later'
# ------------------------------------------------------------------------------------------


@app.route('/')
def index():
    """Renders the index page."""
    return render_template('index.html',), 200

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
