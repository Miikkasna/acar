import numpy
import time
import cv2
from logger import DB_logger

# set up database logger
log = DB_logger(batch=True, batch_size=50)
log.set_new_testcase()

# define camera
cap = cv2.VideoCapture(0)


def main():
    # init last time
    last_time = time.time()
    while True:
        time.sleep(0.05)

        # get camera frame
        ret, frame = cap.read()
        # write image to apache server
        #cv2.imwrite('/var/www/html/image.jpg', frame)


        # log delta time
        interval = (time.time()-last_time)*1000
        last_time = time.time()
        log.log_performance(interval)



if __name__ == "__main__":
    main()