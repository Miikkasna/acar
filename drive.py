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
cap.set(cv2.CAP_PROP_FPS, 30)

# define driver agent
driver = AI()

# define number of anchor points
anchors = 3

# define limits
min_loop_time = 0.04 # s
min_plot_time = 1.5 # s, align with dashboard.html interval
speed_limit = 0.05 # m/s

# initialize metrics
n_points = 20
met = Metrics(n_points)
# loop time
met.add_metric('Loop time', xaxis={'range':[0, n_points], 'title':'Time'}, yaxis={'range':[0, 1000], 'title':'ms'})
met.add_series('Loop time', 'real loop time', 'lines')
met.add_series('Loop time', 'min loop time', 'lines', constant=min_loop_time*1000)
# speed
met.add_metric('Speed', xaxis={'range':[0, n_points], 'title':'Time'}, yaxis={'range':[0, 5], 'title':'m/s'})
met.add_series('Speed', 'Current speed', 'lines')
# distance
met.add_metric('Distance', xaxis={'range':[0, n_points], 'title':'Time'}, yaxis={'range':[0, 20], 'title':'m'})
met.add_series('Distance', 'Cumulative distance', 'lines')
# battery
met.add_metric('Battery', xaxis={'range':[n_points-1.5, n_points-0.5], 'showticklabels':False}, yaxis={'range':[0, 100], 'title':'%'}, stack=True)
risk_zone = 20
met.add_series('Battery', 'Risk zone', 'bar', constant=risk_zone)
met.add_series('Battery', 'Battery charge', 'bar')



def main():
    # init runtime variables
    last_time = time.time()
    last_plot_time = time.time()
    dt = 1.0 # non zero initialization
    while True:
        # get camera frame
        ret, frame = cap.read()
        #process image and get input features
        try:
            res, features = ip.process_image(frame, features=True, anchors=anchors)
        except:
            res, features = frame, {'direction_angle': 0}
        # update stream
        web_server.set_stream_data(res, 'video')

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
        met.update_metric('Loop time', dt*1000)
        met.update_metric('Speed', driver.car.speed)
        met.update_metric('Distance', driver.car.distance)
        met.update_metric('Battery', driver.car.battery_charge - risk_zone, series_number=1)
        if (time.time()-last_plot_time) > min_plot_time:
            met.update_chart_data()
            last_plot_time = time.time()
            web_server.set_stream_data(met.json_charts, 'charts')

        # log run time data
        dt = (time.time()-last_time)
        log.log_data(loop_time=dt*1000, 
            battery_voltage=driver.car.battery_voltage,
            distance=0,
            speed=driver.car.speed,
            throttle=driver.car.throttle
        )

        # wait until minimum looptime
        while (time.time()-last_time) < min_loop_time:
            pass
        last_time = time.time()

        # connection check
        if connection_check:
            if (time.time() - web_server.stamp) > 3.5:
                raise Exception('connection not verified')

def shutdown():
    driver.stop_motor()
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