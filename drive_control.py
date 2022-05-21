import RPi.GPIO as GPIO
import xbox
import time
import serial
from neural_netwok import NeuralNetwork
import numpy as np

# setup GPIO
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system

# define GPIO board pins
servo_pin = 16			# PWM pin connected
mcu_pin = 18		# PWM pin connected

# define PWM setup
pwm_freq = 200
GPIO.setup(servo_pin,GPIO.OUT)
servo_pwm = GPIO.PWM(servo_pin,pwm_freq)		#create PWM instance with frequency
servo_pwm.start(0)				#start PWM of required Duty Cycle
GPIO.setup(mcu_pin,GPIO.OUT)
mcu_pwm = GPIO.PWM(mcu_pin,pwm_freq)		#create PWM instance with frequency
mcu_pwm.start(0)				#start PWM of required Duty Cycle 

# initialize serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.01)
ser.reset_input_buffer()

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class Car():
    def __init__(self):
        self.speed = 0
        self.distance = 0
        self.direction_angle = 0
        self.motor_current = 0
        self.battery_voltage = 0
        self.battery_charge = 0
        self.throttle = 0
        self.steering = 0

class Driver():
    def __init__(self):
        self.car = Car()
        self.MAX_CURVE_ANGLE = 60

    def __init_subclass__(self):
        Driver.__init__(self)

    def calc_pulse_width(self, control):
        return map(control, -1, 1, 950e-6, 1950e-6)

    def calc_duty_cycle(self, pulse_width):
        T = 1/pwm_freq
        return pulse_width/T

    def set_servo(self, duty_cycle):
        servo_pwm.ChangeDutyCycle(duty_cycle*100) #provide duty cycle in the range 0-100

    def set_mcu(self, duty_cycle):
        mcu_pwm.ChangeDutyCycle(duty_cycle*100) #provide duty cycle in the range 0-100

    def steer(self): # control; 0=middle, -1=full rigth 1=full left
        control = self.car.steering
        pw = self.calc_pulse_width(control*(-1))
        dc = self.calc_duty_cycle(pw)
        self.set_servo(dc)

    def stop_motor(self):
        mcu_pwm.start(0)

    def throttle(self): # control; 0=neutral, -1=full reverse 1=full throttle
        control = self.car.throttle
        pw = self.calc_pulse_width(control*(-1)) # switch polarization
        dc = self.calc_duty_cycle(pw)
        self.set_mcu(dc)

    def calc_inputs(self, dt, features=None):
        while ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip().split(';')
            self.car.battery_voltage = float(data[0])
            self.car.speed = float(data[1])
        self.car.battery_charge = map(self.car.battery_voltage, 4.6, 8.4, 0, 100)
        self.car.distance += self.car.speed*dt
        self.car.direction_angle = features['direction_angle']


class GamePad(Driver):
    def __init__(self):
        self.joy = xbox.Joystick()
        print('GamePad selected')

    def set_actions(self):
        _, self.car.throttle = self.joy.rightStick()
        self.car.steering, _ = self.joy.leftStick()

class Idle(Driver):
    def __init__(self):
        print('Idle selected')

    def set_actions(self):
        self.car.throttle = 0
        self.car.steering = 0

class AI(Driver):
    def __init__(self):
        print('AI selected')
        n_inputs, n_outputs = 2, 2
        self.agent = NeuralNetwork(n_inputs, [4], n_outputs)
        self.agent.network = np.load('trained_agent.npy', allow_pickle=True)
        self.speed_correction = 10.0
        self.throttle_correction = 0.01
        self.dir_switch = -1

    def set_actions(self):
        def limit(val):
            if val > 1.0:
                return 1.0
            elif val < -1.0:
                return -1.0
            else:
                return val
        inputs = [self.car.speed*self.speed_correction, self.dir_switch*self.car.direction_angle/self.MAX_CURVE_ANGLE]
        output = self.agent.forward_propagate(inputs)
        
        self.car.steering = limit(float(output[0]))
        self.car.throttle = limit(float(output[1]*self.throttle_correction))

class DumDum(Driver):
    def __init__(self):
        print('DumDum selected')

    def set_actions(self):
        self.car.throttle = 0.04
        self.car.steering = -self.car.direction_angle/self.MAX_CURVE_ANGLE
        if abs(self.car.steering) > 1.0:
            self.car.steering = self.car.steering/abs(self.car.steering)