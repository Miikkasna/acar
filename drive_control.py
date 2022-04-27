import RPi.GPIO as GPIO
import xbox
import time

# setup GPIO
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system

# define GPIO board pins
enc_pin = 15
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

# define encoder interrupt event
GPIO.setup(enc_pin, GPIO.IN)
counter = 0
def rotation_decode(enc_pin):
    global counter
    if GPIO.input(enc_pin)==1:
        counter += 1
GPIO.add_event_detect(enc_pin, GPIO.RISING, callback=rotation_decode)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class Driver():
    def __init__(self):
        self.speed = 0
    def calc_pulse_width(self, control):
        return map(control, -1, 1, 950e-6, 2000e-6)

    def calc_duty_cycle(self, pulse_width):
        T = 1/pwm_freq
        return pulse_width/T

    def set_servo(self, duty_cycle):
        servo_pwm.ChangeDutyCycle(duty_cycle*100) #provide duty cycle in the range 0-100

    def set_mcu(self, duty_cycle):
        mcu_pwm.ChangeDutyCycle(duty_cycle*100) #provide duty cycle in the range 0-100

    def steer(self, control): # control; 0=middle, -1=full rigth 1=full left
        pw = self.calc_pulse_width(control*(-1))
        dc = self.calc_duty_cycle(pw)
        self.set_servo(dc)

    def throttle(self, control): # control; 0=neutral, -1=full reverse 1=full throttle
        pw = self.calc_pulse_width(control*(-1)) # switch polarization
        dc = self.calc_duty_cycle(pw)
        self.set_mcu(dc)

    def calc_inputs(self, dt):
        global counter
        distance = counter/357.0 # calibrated as meters
        self.speed = distance / dt
        counter = 0


class GamePad(Driver):
    def __init__(self):
        self.joy = xbox.Joystick()
        print('GamePad selected')

    def get_steering(self):
        steering, _ = self.joy.leftStick()
        return steering

    def get_throttle(self):
        _, throttle = self.joy.rightStick()
        return throttle

class Idle(Driver):
    def __init__(self):
        print('Idle selected')

    def get_steering(self):
        return 0

    def get_throttle(self):
        return 0