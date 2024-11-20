#!/usr/bin/env python3
# udp_server_with_cmd_vel.py
import socket
import rospy
from geometry_msgs.msg import Twist
import sys

# ROS ³ëµå ÃÊ±âÈ­
rospy.init_node('udp_cmd_vel_server', anonymous=True)

# /cmd_vel ÅäÇÈ ÆÛºí¸®¼Å »ý¼º
pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
cmd = Twist()

# UDP ¼­¹ö ¼³Á¤
HOST = '0.0.0.0'  
PORT = 65432      

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("UDP start & waiting...")

try:
    while not rospy.is_shutdown():
        data, addr = server_socket.recvfrom(1024)  # ÃÖ´ë 1024 ¹ÙÀÌÆ® ¼ö½Å
        chch = data.decode().strip()  # ¼ö½ÅµÈ µ¥ÀÌÅÍ¸¦ ¹®ÀÚ¿­·Î º¯È¯ÇÏ°í °ø¹é Á¦°Å
        print(f"Received from {addr}: {chch}")

        # chch °ª¿¡ µû¸¥ µ¿ÀÛ ¼³Á¤
        if chch == '0':
            # cmd_velÀ» 0À¸·Î ¼³Á¤
            cmd.linear.x = 0.0
            cmd.linear.y = 0.0
            cmd.linear.z = 0.0
            cmd.angular.x = 0.0
            cmd.angular.y = 0.0
            cmd.angular.z = 0.0
            pub.publish(cmd)
            print("cmd_vel set zero")

        elif chch == '1':
            # cmd.linear.y¿¡ -1.0 ¼³Á¤
            cmd.linear.x = 0.0
            cmd.linear.y = -1.0
            cmd.linear.z = 0.0
            cmd.angular.x = 0.0
            cmd.angular.y = 0.0
            cmd.angular.z = 0.0
            pub.publish(cmd)
            print("side is 1 & move right!")

        elif chch == '2':
            # ¼­¹ö Á¾·á ¹× ÇÁ·Î±×·¥ Á¾·á
            print("received 2 & closing move_side.py")
            server_socket.close()  # ¼ÒÄÏÀ» ´Ý°í
            sys.exit("Exiting due to command 2")  # ÇÁ·Î±×·¥ Á¾·á

        else:
            print("received:", chch)

except KeyboardInterrupt:
    print("keyboard interrupt")

finally:
    server_socket.close()  # ÇÁ·Î±×·¥ Á¾·á Àü ¼ÒÄÏÀ» ´Ý½À´Ï´Ù.
    print("UDP server socket closed")
