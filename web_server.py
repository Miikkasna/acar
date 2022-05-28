from flask import Flask, Response, send_file, request, render_template
import cv2
import numpy as np
import threading, os
from datetime import datetime
import logging, time

# define connection flags
stamp = time.time() + 10.0
force_shutdown = False

blank = np.zeros([400,400,3],dtype=np.uint8)
site_data = {'video': blank.copy(), 'charts': None}
app = Flask(__name__)
# disable console logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

@app.route("/")
def index():
    html = '''<h2>Welcome to Acar web server</h2><br>
    <a href=/stream>stream</a><br>
    <a href=/dashboard>dashboard</a><br>
    <a href=/snap_shot>snap_shot</a><br>
    <a href=/connection>connection</a><br>
    '''
    return html

def set_data(data, stream):
    site_data[stream] = data

def img_to_bytes(img):
    return cv2.imencode('.jpg', img)[1].tobytes()

def get_video():
    while True:
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img_to_bytes(site_data['video']) + b'\r\n')

@app.route("/stream")
def stream():
    return Response(get_video(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/chart_data")
def chart_data():
    return Response(site_data['charts'], mimetype='text/json')

@app.route('/dashboard')   
def dashboard():
    return render_template('dashboard.html')

@app.route('/connection')   
def connection():
    global stamp
    stamp = time.time()
    return render_template('connection.html')

def shutdown_server():
    global force_shutdown
    force_shutdown = True
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')   
def shutdown():
    shutdown_server()

def run_app():
    app.run('0.0.0.0', debug=False)

# start stream thread
server = threading.Thread(target=run_app)
server.start()

