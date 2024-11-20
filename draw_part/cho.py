import RPi.GPIO as GPIO
import time
import socket
import signal
import sys
import atexit

SERVER_IP = '172.20.10.4'  
PORT = 50001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("AkibaTV HC-SR04 Start")
message = "g"
GPIO.setmode(GPIO.BCM)
# Yellow : Pin 11 : 17(Trig)
GPIO.setup(17, GPIO.OUT)
# White : Pin 12 : 27(Echo)
GPIO.setup(27, GPIO.IN)


atexit.register(GPIO.cleanup)
try:
    while True:
        GPIO.output(17, False)
        time.sleep(0.5)

        GPIO.output(17, True)
        time.sleep(0.00001)
        GPIO.output(17, False)

        while GPIO.input(27) == 0:
            start = time.time()

        while GPIO.input(27) == 1:
            stop = time.time()

        time_interval = stop - start
        distance = time_interval * 17000
        distance = round(distance, 2)

        print("Distance => ", distance, "cm")
        if distance <= 20:
            message = "W"  
            client_socket.sendto(message.encode(), (SERVER_IP, PORT))
            print("warning")
            time.sleep(1.5)
            
        else:
            ago = message
            message = "S"
            if ago == "S":
                print("")
            else:
                client_socket.sendto(message.encode(), (SERVER_IP, PORT))
                print("nono")
                    
finally:
        GPIO.cleanup()        
    
