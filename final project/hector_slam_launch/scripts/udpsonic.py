#!/usr/bin/env python3
# udp_server_with_cmd_vel.py
import socket
import rospy
from geometry_msgs.msg import Twist
import mysql.connector
import subprocess
import sys
import time

# ROS ³ëµå ÃÊ±âÈ­
rospy.init_node('udp_sonic_cmd_vel_server', anonymous=True)

# /cmd_vel ÅäÇÈ ÆÛºí¸®¼Å »ý¼º
pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
cmd = Twist()

# UDP ¼­¹ö ¼³Á¤
HOST = '0.0.0.0'  
PORT = 50001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("UDP sonic start & waiting...")
