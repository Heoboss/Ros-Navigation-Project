from gpiozero import Motor
import time
import RPi.GPIO as GPIO 

def pin_num(pin1, pin2):
    
    return Motor(forward=pin1, backward=pin2)

def motor_control(motor, direction, speed):
    
    if direction == 'forward':
        motor.forward(speed=speed)
    elif direction == 'backward':
        motor.backward(speed=speed)

def motor_stop(motor):
    motor.stop()
    

def main():
   motor = pin_num(pin1=23, pin2=24)
   i=1
    

   while True:
        motor_control(motor, direction='forward', speed=1)
        time.sleep(26)
        motor_control(motor, direction='backward', speed=1)
        time.sleep(26)
        
        
if __name__ == "__main__":
    main()

