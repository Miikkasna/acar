import pigpio
import xbox
import time
import serial
from neural_netwok import NeuralNetwork
import numpy as np


# define GPIO board pins
servo_pin = 12			# PWM pin connected
mcu_pin = 13		# PWM pin connected

# setup GPIO
gpio = pigpio.pi()
gpio.set_mode(servo_pin, pigpio.OUTPUT)
gpio.set_mode(mcu_pin, pigpio.OUTPUT)

# define PWM setup
pwm_freq = 50
gpio.set_PWM_frequency(servo_pin, pwm_freq)
gpio.set_PWM_frequency(mcu_pin, pwm_freq)

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
        self.LIMIT_CONTROL = 0.6 # %

    def __init_subclass__(self):
        Driver.__init__(self)

    def calc_pulse_width(self, control):
        return map(control, -1, 1, 1000, 2000)

    def calc_duty_cycle(self, pulse_width):
        T = 1.00000/float(pwm_freq)
        return int(pulse_width/T)

    def set_servo(self, duty_cycle):
        gpio.hardware_PWM(servo_pin, pwm_freq, duty_cycle)

    def set_mcu(self, duty_cycle):
        gpio.hardware_PWM(mcu_pin, pwm_freq, duty_cycle)

    def steer(self): # control; 0=middle, -1=full rigth 1=full left
        control = self.car.steering
        pw = self.calc_pulse_width(control*(-1))
        dc = self.calc_duty_cycle(pw)
        self.set_servo(dc)

    def stop_motor(self):
        gpio.hardware_PWM(mcu_pin, pwm_freq, 0)

    def throttle(self): # control; 0=neutral, -1=full reverse 1=full throttle
        control = self.car.throttle
        pw = self.calc_pulse_width(control*(-1)) # switch polarization
        dc = self.calc_duty_cycle(pw)
        self.set_mcu(dc)

    def update_state(self, dt, features):
        while ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip().split(';')
            self.car.battery_voltage = float(data[0])
            self.car.speed = float(data[1])
        self.car.battery_charge = map(self.car.battery_voltage, 5.1, 8.4, 0, 100)
        self.car.distance += self.car.speed*dt
        self.car.direction_angle = features['direction_angle']

    def limit(self, val):
        lim = self.LIMIT_CONTROL
        if val > lim:
            return lim
        elif val < -lim:
            return -lim
        else:
            return val

class GamePad(Driver):
    def __init__(self):
        self.joy = xbox.Joystick()
        print('GamePad selected')

    def set_actions(self):
        _, self.car.throttle = self.joy.rightStick()
        self.car.steering, _ = self.joy.leftStick()

class Idle(Driver):
    def __init__(self):
        print('Idle driver selected')

    def set_actions(self):
        self.car.throttle = 0
        self.car.steering = 0

class AI(Driver):
    def __init__(self):
        print('AI driver selected')
        n_inputs, n_outputs = 2, 2
        self.agent = NeuralNetwork(n_inputs, [4], n_outputs)
        self.agent.network = np.load('trained_agent.npy', allow_pickle=True)
        self.speed_correction = 4.0
        self.throttle_correction = 0.6
        self.steering_correction = 0.6
        self.dir_switch = 1

    def set_actions(self):
        angle = self.dir_switch*self.car.direction_angle/self.MAX_CURVE_ANGLE
        speed = self.car.speed*self.speed_correction
        inputs = [speed, angle]
        output = self.agent.forward_propagate(inputs)

        self.car.steering = self.limit(float(output[0])*self.steering_correction)
        self.car.throttle = self.limit(float(output[1]*self.throttle_correction))

class DumDum(Driver):
    def __init__(self):
        print('DumDum driver selected')

    def set_actions(self):
        self.car.throttle = 0.03
        self.car.steering = self.limit(-self.car.direction_angle/self.MAX_CURVE_ANGLE)
