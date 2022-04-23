from flask import Flask, Response, send_file, request, render_template
import cv2
import numpy as np
import threading
from datetime import datetime

image = np.zeros([400,400,3],dtype=np.uint8)
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World"

def set_image(img):
    global image
    image = img

def img_to_bytes(img):
    return cv2.imencode('.jpg', img)[1].tobytes()

def get_image():
    while True:
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img_to_bytes(image) + b'\r\n')
@app.route("/stream")
def stream():
    return Response(get_image(), mimetype="multipart/x-mixed-replace; boundary=frame")
    
@app.route("/snap_shot", methods=['GET', 'POST'])
def snap_shot():
    if request.method == 'POST':
        if request.form.get('action1') == 'Take snap shot':
            img_path = 'static/{}.jpg'.format(datetime.now())
            cv2.imwrite(img_path, image)
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


# start stream thread
threading.Thread(target=lambda: app.run('0.0.0.0', debug=False)).start()

