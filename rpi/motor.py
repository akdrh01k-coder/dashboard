from gpiozero import Motor 
import time 

motor = Motor(forward=20, backward=21)

while True:
    print('forward')
    motor.forward()
    time.sleep(5)
    
    print('backward')
    motor.backward()
    time.sleep(5)
