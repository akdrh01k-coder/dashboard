import RPi.GPIO as GPIO
import time
import sys
import termios
import tty

ENA = 32   # GPIO12 (PWM)
IN1 = 29   # GPIO5
IN2 = 31   # GPIO6

ENB = 33   # GPIO13 (PWM)
IN3 = 38   # GPIO20
IN4 = 40   # GPIO21

PWM_FREQ = 1000  # 1kHz PWM 

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def setup():
    GPIO.setmode(GPIO.BOARD)
    for pin in [IN1, IN2, IN3, IN4, ENA, ENB]:
        GPIO.setup(pin, GPIO.OUT)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

    pwmA = GPIO.PWM(ENA, PWM_FREQ)
    pwmB = GPIO.PWM(ENB, PWM_FREQ)
    pwmA.start(0)
    pwmB.start(0)
    return pwmA, pwmB

def forward(pwmA, pwmB, speed=100):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)

def stop(pwmA, pwmB):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

if __name__ == "__main__":
    pwmA, pwmB = setup()
    print("start: 'w', 's' → stop, 'q' → quit")
    try:        
        while True:
            key = get_key()
            if key == 'w':
                print("start!")
                forward(pwmA, pwmB, speed=100)
            elif key == 's':
                print("stop!")
                stop(pwmA, pwmB)
            elif key == 'q':
                print("quit.")
                break
    except KeyboardInterrupt:
        pass
    finally:
        stop(pwmA, pwmB)
        pwmA.stop()
        pwmB.stop()
        GPIO.cleanup()
