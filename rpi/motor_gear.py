import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pwm_pin = 3
in1_pin = 5
in2_pin = 7

GPIO.setup(pwm_pin, GPIO.OUT)
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)

pwm_motor = GPIO.PWM(pwm_pin, 100)
pwm_motor.start(0)

while True:
    gear = input("press w: go s: stop x: back")
    if gear == "s":
        pwm_motor.ChangeDutyCycle(0)
    elif gear == "w":
        pwm_motor.ChangeDutyCycle(100)
        GPIO.output(in1_pin, True)
        GPIO.output(in2_pin, False)
    elif gear == "x":
        pwm_motor.ChangeDutyCycle(100)
        GPIO.output(in1_pin, False)
        GPIO.output(in2_pin, True)
    else:
        GPIO.cleanup()
        break
