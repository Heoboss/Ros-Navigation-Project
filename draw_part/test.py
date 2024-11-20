import RPi.GPIO as GPIO     
from time import sleep      

servo_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)  
servo = GPIO.PWM(servo_pin, 50)  
servo.start(0)  
servo_min_duty = 3               
servo_max_duty = 12  
current_duty = servo_min_duty            
 # servo rotate clock
def set_servo_degree(degree,speed):    
    if degree > 180:
        degree = 180
    elif degree < 0:
        degree = 180 + degree
        
    global current_duty
    target_duty = servo_min_duty+(degree*(servo_max_duty-servo_min_duty)/180.0)
    
    
    if current_duty < target_duty:
        step = 0.08
        while current_duty < target_duty:
            current_duty += step
            if current_duty > target_duty:
                current_duty = target_duty
            GPIO.setup(servo_pin, GPIO.OUT)  
            servo.ChangeDutyCycle(current_duty)
            sleep(0.01 * speed)
            GPIO.setup(servo_pin, GPIO.IN)
    else:
        step = 0.08
        while current_duty > target_duty:
            current_duty -= step
            if current_duty < target_duty:
                current_duty = target_duty
            GPIO.setup(servo_pin, GPIO.OUT)  
            servo.ChangeDutyCycle(current_duty)
            sleep(0.01 * speed)   
            GPIO.setup(servo_pin, GPIO.IN)
            
    current_duty = target_duty
