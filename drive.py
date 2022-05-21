import time, sys
import cv2
from logger import DB_logger
import numpy as np
import urllib.request
from drive_control import Idle, GamePad, AI, DumDum
import web_server
import image_process as ip
from metrics import Metrics

# define connection check variable
connection_check = False

# set up database logger
log = DB_logger(batch=False, batch_size=50)
log.set_new_testcase()

# define camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)
cap.set(cv2.CAP_PROP_FPS, 60)

# define driver agent
driver = DumDum()

# define limits
min_loop_time = 0.1
min_plot_time = 0.950 # align with dashboard.html interval
speed_limit = 0.05 # m/s

# initialize metrics
met = Metrics(n_points=20)
met.add_metric('loop time', 'ms', 'line', (0, 500), constant={'name':'Min loop time', 'value':min_loop_time*1000})
met.add_metric('speed', 'm/s', 'line', (0, 5))
met.add_metric('distance', 'm', 'bar', (0, 20))
met.add_metric('battery', '%', 'stackbar', (0, 100), constant={'name':'Risk zone', 'value':20})

def main():
    # init last time
    last_time = time.time()
    last_plot_time = time.time()
    dt = 1.0 # non zero initialization
    while True:
        time.sleep(0.03)

        # get camera frame
        ret, frame = cap.read()
        #process image and get input features
        try:
            res, features = ip.process_image(frame, features=True)
        except:
            res, features = frame, {'direction_angle': 0}
        # update stream
        web_server.set_image(res, 'video')

        # calculate inputs
        driver.calc_inputs(dt, features)

        # set actions
        driver.set_actions()

        # execute actions
        driver.steer()
        driver.throttle()

        # limit speed
        if driver.car.speed > speed_limit:
            driver.stop_motor()
        
        # update metrics
        met.update_metric('loop time', dt*1000)
        met.update_metric('speed', driver.car.speed)
        met.update_metric('distance', driver.car.distance)
        met.update_metric('battery', driver.car.battery_charge)
        if (time.time()-last_plot_time) > min_plot_time:
            met.plot_metrics()
            last_plot_time = time.time()
            web_server.set_image(met.json_charts, 'charts')

        # log run time data
        dt = (time.time()-last_time)
        log.log_data(loop_time=dt*1000, 
            battery_voltage=driver.car.battery_voltage,
            distance=0,
            speed=driver.car.speed,
            throttle=driver.car.throttle
        )

        while (time.time()-last_time) < min_loop_time:
            pass
        last_time = time.time()

        # connection check
        if connection_check:
            if (time.time() - web_server.stamp) > 3.5:
                raise Exception('connection not verified')

def shutdown():
    try:
        contents = urllib.request.urlopen("http://localhost:5000/shutdown").read()
    except:
        print("Server closed")
    raise Exception('Shutdown')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
        shutdown()
    except Exception as e:
        print(e)
        shutdown()