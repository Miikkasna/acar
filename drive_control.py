import RPi.GPIO as GPIO
import xbox

pwm_freq = 200
servo_pin = 18
motor_pin = 17


servo_pin = 16			# PWM pin connected
mcu_pin = 18		# PWM pin connected
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system
GPIO.setup(servo_pin,GPIO.OUT)
servo_pwm = GPIO.PWM(servo_pin,pwm_freq)		#create PWM instance with frequency
servo_pwm.start(0)				#start PWM of required Duty Cycle
GPIO.setup(mcu_pin,GPIO.OUT)
mcu_pwm = GPIO.PWM(mcu_pin,pwm_freq)		#create PWM instance with frequency
mcu_pwm.start(0)				#start PWM of required Duty Cycle 


def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class Driver():
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
        pw = self.calc_pulse_width(control)
        dc = self.calc_duty_cycle(pw)
        self.set_servo(dc)

    def throttle(self, control): # control; 0=neutral, -1=full reverse 1=full throttle
        pw = self.calc_pulse_width(control*(-1)) # switch polarization
        dc = self.calc_duty_cycle(pw)
        self.set_mcu(dc)

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
