import numpy
import time
import cv2
from logger import DB_logger
import numpy as np
from flask import Flask, Response, send_file
from drive_control import GamePad


# set up database logger
log = DB_logger(batch=True, batch_size=50)
log.set_new_testcase()

# define camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) # depends on fourcc available camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)
cap.set(cv2.CAP_PROP_FPS, 60)


#setup video stream
import video_stream


def main():
    # init last time
    last_time = time.time()
    driver = GamePad()
    while True:
        time.sleep(0.01)

        # get camera frame
        ret, frame = cap.read()
        # update stream
        video_stream.set_image(frame)

        #set driving parameters
        steering = driver.get_steering()
        throttle = driver.get_throttle()
        driver.steer(steering)
        driver.throttle(throttle)
        
        # log delta time
        interval = (time.time()-last_time)*1000
        last_time = time.time()
        log.log_performance(interval)


if __name__ == "__main__":
    main()