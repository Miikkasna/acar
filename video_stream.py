from flask import Flask, Response, send_file
import cv2
import numpy as np
import threading

image = cv2.imencode('.jpg', np.zeros([400,400,3],dtype=np.uint8))[1].tobytes()
app = Flask(__name__)
@app.route("/")
def index():
    return "Hello World"
def set_image(img):
    global image
    image = cv2.imencode('.jpg', img)[1].tobytes()
def get_image():
    while True:
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
@app.route("/stream")
def stream():
    return Response(get_image(), mimetype="multipart/x-mixed-replace; boundary=frame")
# start stream thread
threading.Thread(target=lambda: app.run('0.0.0.0', debug=False)).start()

