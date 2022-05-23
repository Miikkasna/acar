from flask import Flask, Response, send_file, request, render_template
import cv2
import numpy as np
import threading, os
from datetime import datetime
import logging, time
import json

# define connection check safety stamp
stamp = time.time() + 10.0

blank = np.zeros([400,400,3],dtype=np.uint8)
images = {'video': blank.copy(), 'charts': None}
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

def set_image(img, stream):
    images[stream] = img

def img_to_bytes(img):
    return cv2.imencode('.jpg', img)[1].tobytes()

def get_image(stream):
    while True:
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img_to_bytes(images[stream]) + b'\r\n')

@app.route("/stream")
def stream():
    return Response(get_image('video'), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/chart_data")
def chart_data():
    data1, data2 = list(np.random.rand(11)*10), list(np.random.rand(11)*10)
    data = {
        'c1': [{'y': data1, 'type':'lines'}, {'y': data2, 'type':'bar'}],
        'c2': [{'y': data2, 'type':'lines'}, {'y': data1, 'type':'bar'}]
        
        }
    data = json.dumps(data, indent = 4)
    return Response(data, mimetype='text/json')
    #return Response(images['charts'], mimetype='text/json')

@app.route('/dashboard')   
def dashboard():
    return render_template('dashboard.html')

@app.route("/snap_shot", methods=['GET', 'POST'])
def snap_shot():
    if request.method == 'POST':
        if request.form.get('action1') == 'Take snap shot':
            stamp = str(datetime.now()).replace(':', '.')
            img_path = 'static/{}.jpg'.format(stamp)
            cv2.imwrite(img_path, images['video'])
            print('snap shot taken')
        else:
            pass
    elif request.method == 'GET':
        return '<form method="post" action="/snap_shot"><input type="submit" value="Take snap shot" name="action1"/></form>'
    html = (
        '''<!DOCTYPE html>
        <html><body>
        <form method="post" action="/snap_shot"><input type="submit" value="Take snap shot" name="action1"/></form>
        <img src="/{}" alt="User Image">
        </body></html>'''.format(img_path)
    )
    return html

@app.route('/connection')   
def connection():
    global stamp
    stamp = time.time()
    return render_template('connection.html')

def shutdown_server():
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

