import time
import cv2
from logger import DB_logger
import urllib.request
from drive_control import Idle, GamePad, AI, DumDum
import image_process as ip
from metrics import Metrics

# set connection check variable
connection_check = False

# init web server
import web_server
web_server.set_param_defaults(ip.params)

# set up database logger
log = DB_logger(batch=True, batch_size=50)
log.set_new_testcase()

# define camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)
cap.set(cv2.CAP_PROP_FPS, 30)

# define driver agent
driver = AI()

# define limits
min_loop_time = 0.04 # s, set so that average loop execution time stays just below minimum
speed_limit = 0.1 # m/s

# initialize metrics
met = Metrics()
# loop time
n_points = int(10.0/min_loop_time)
met.add_metric('Loop time', n_points, xaxis={'range':[0, n_points], 'title':'Time'}, yaxis={'range':[0, 500], 'title':'ms'})
met.add_series('Loop time', 'Real loop time', 'lines')
met.add_series('Loop time', 'Min loop time', 'lines', constant=min_loop_time*1000)
# speed
n_points = int(10.0/min_loop_time)
met.add_metric('Speed', n_points, xaxis={'range':[0, n_points], 'title':'Time'}, yaxis={'range':[0, 5], 'title':'m/s'})
met.add_series('Speed', 'Current speed', 'lines')
# distance
n_points = int(20.0/min_loop_time)
met.add_metric('Distance', n_points, xaxis={'range':[0, n_points], 'title':'Time'}, yaxis={'range':[0, 20], 'title':'m'})
met.add_series('Distance', 'Cumulative distance', 'lines')
# battery
n_points = 10
met.add_metric('Battery', n_points, xaxis={'range':[n_points-1.5, n_points-0.5], 'showticklabels':False}, yaxis={'range':[0, 100], 'title':'%'}, stack=True)
risk_zone = 20
met.add_series('Battery', 'Risk zone', 'bar', constant=risk_zone)
met.add_series('Battery', 'Battery charge', 'bar')


def main():
    # init runtime variables
    last_time = time.time()
    dt = min_loop_time # non zero initialization

    while True:
        # update parameters
        ip.update_params(web_server.params)

        # get camera frame
        ret, frame = cap.read()

        # process image and get input features
        try:
            res, features = ip.process_image(frame)
        except Exception as e:
            res, features = frame, {'direction_angle': 0}
            
        # update stream
        web_server.set_data(res, 'video')

        # update driver state
        driver.update_state(dt, features)

        # set actions
        driver.set_actions()

        # execute actions
        driver.steer()
        driver.throttle()

        # limit speed
        if driver.car.speed > speed_limit:
            driver.stop_motor()

        # calculate delta time
        dt = (time.time()-last_time)

        # update metrics
        met.update_metric('Loop time', dt*1000)
        met.update_metric('Speed', driver.car.speed)
        met.update_metric('Distance', driver.car.distance)
        met.update_metric('Battery', driver.car.battery_charge - risk_zone, series_number=1)
        met.update_chart_data()
        web_server.set_data(met.json_charts, 'charts')

        # log run time data
        log.log_data(loop_time=dt*1000, 
            battery_voltage=float(driver.car.battery_voltage),
            distance=float(driver.car.distance),
            speed=float(driver.car.speed),
            angle_offset=float(driver.car.direction_angle),
            steering=float(driver.car.steering),
            throttle=float(driver.car.throttle)
        )

        # wait until minimum looptime
        while (time.time()-last_time) < min_loop_time:
            pass

        # update last time
        last_time = time.time()

        # server control check
        if connection_check:
            if (time.time() - web_server.stamp) > 2.5:
                raise Exception('connection not verified')
        if web_server.force_shutdown:
            raise Exception('Force shutdown')

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