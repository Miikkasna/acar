import numpy
import time
import cv2
from logger import DB_logger
import numpy as np
from flask import Flask, Response, send_file
from drive_control import Idle
import web_server

# set up database logger
log = DB_logger(batch=True, batch_size=50)
log.set_new_testcase()

# define camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) # depends on fourcc available camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)
cap.set(cv2.CAP_PROP_FPS, 60)

# define driver agent
driver = Idle()

def main():
    # init last time
    last_time = time.time()
    dt = 0.02 # non zero initialization
    while True:
        time.sleep(0.1)

        # get camera frame
        ret, frame = cap.read()
        # update stream
        web_server.set_video_image(frame)

        # calculate inputs
        driver.calc_inputs(dt)

        # set driving parameters
        steering = driver.get_steering()
        throttle = driver.get_throttle()
        driver.steer(steering)
        driver.throttle(throttle)
        
        # log delta time
        dt = (time.time()-last_time)
        last_time = time.time()
        log.log_performance(dt*1000) # save as milliseconds




if __name__ == "__main__":
    main()