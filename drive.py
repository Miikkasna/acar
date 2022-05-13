import numpy
import time
import cv2
from logger import DB_logger
import numpy as np
from flask import Flask, Response, send_file
from drive_control import Idle, GamePad
import web_server
import image_process as ip
from metrics import Metrics

# set up database logger
log = DB_logger(batch=True, batch_size=50)
log.set_new_testcase()

# define camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)
cap.set(cv2.CAP_PROP_FPS, 60)

# define driver agent
driver = Idle()

# define minimum loop time
min_loop_time = 0.120

# initialize metrics
met = Metrics(n_points=20)
met.add_metric('loop time', 'ms', 'line', (0, 500), constant={'name':'Min loop time', 'value':min_loop_time*1000})
met.add_metric('speed', 'm/s', 'line', (0, 5))

def main():
    # init last time
    last_time = time.time()
    dt = 0.02 # non zero initialization
    while True:
        time.sleep(0.03)

        # get camera frame
        ret, frame = cap.read()
        #process image
        try:
            res = ip.process_image(frame, features=False)
        except:
            res = frame
        # update stream
        web_server.set_image(res, 'video')

        # calculate inputs
        driver.calc_inputs(dt)

        # set driving parameters
        steering = driver.get_steering()
        throttle = driver.get_throttle()
        driver.steer(steering)
        driver.throttle(throttle)
        
        # update metrics
        met.update_metric('loop time', dt*1000)
        met.update_metric('speed', driver.car.speed)
        met.plot_metrics()
        web_server.set_image(met.json_charts, 'charts')

        # log delta time
        dt = (time.time()-last_time)
        log.log_performance(dt*1000) # save as milliseconds

        while (time.time()-last_time) < min_loop_time:
            pass
        last_time = time.time()


if __name__ == "__main__":
    main()