#!/usr/bin/env python3
# udp_server_with_cmd_vel.py
import socket
import rospy
from geometry_msgs.msg import Twist
import mysql.connector
import subprocess
import sys
import time

def connect_to_db():
    connection = mysql.connector.connect(
        host='192.203.145.54',
        user='pi',
        password='1234',
        database='booksearch',
        auth_plugin='mysql_native_password'
    )
    return connection
    
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
        # UDP ¸Þ½ÃÁö ¼ö½Å ´ë±â
        data, addr = server_socket.recvfrom(1024)
        chch = data.decode().strip()
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
            time.sleep(0.1)
            cmd.linear.y = 0.0
            pub.publish(cmd)
        elif chch == '2':
            print("received 2 & closing server and checking database")
            print("received 2: moving forward briefly, then checking database")
            cmd.linear.x = 1.0
            pub.publish(cmd)
            time.sleep(1.5)  # 0.5ÃÊ µ¿¾È ÀÌµ¿ À¯Áö
            cmd.linear.x = 0.0
            pub.publish(cmd)
            print("cmd_vel forward motion reset to zero")
            server_socket.close()
            
            # µ¥ÀÌÅÍº£ÀÌ½º È®ÀÎ ·çÇÁ
            while not rospy.is_shutdown():
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("SELECT go FROM ros LIMIT 1;")
                go_row = cursor.fetchone()
                
                print("go checking: ", go_row[0])
                cursor.close()
                connection.close()

               
                
                # go °ªÀÌ 2ÀÌ¸é go_to_initial.py ½ÇÇà ÈÄ Á¾·á
                if go_row is not None and go_row[0] == '2':
                    print("go value is 2 in DB, executing go_to_initial.py")
                    print("backward")
                    cmd.linear.x = -0.4
                    cmd.angular.z = 0.3
                    pub.publish(cmd)
                    time.sleep(1.8)  # 0.5ÃÊ µ¿¾È ÀÌµ¿ À¯Áö
                    cmd.linear.x = 0.0
                    cmd.angular.z = 0.0
                    pub.publish(cmd)
                    subprocess.Popen(["rosrun", "hector_slam_launch", "go_to_initial_1.py"])
                    sys.exit("Exiting after executing go_to_initial_1.py")
                elif go_row is not None and go_row[0] == '3':
                    print("backward go_row 3")
                    cmd.linear.x = -0.4
                    pub.publish(cmd)
                    time.sleep(1)
                    cmd.linear.x = 0.0
                    pub.publish(cmd)
                    print("backward off")
                    connection = connect_to_db()
                    cursor = connection.cursor()
                    cursor.execute("UPDATE ros SET go = '0' LIMIT 1;")
                    connection.commit()
    
                    cursor.close()
                    connection.close()
                time.sleep(1)  # µ¥ÀÌÅÍº£ÀÌ½º È®ÀÎ ÁÖ±â
        else:
            print("received:", chch)

except KeyboardInterrupt:
    print("keyboard interrupt")

finally:
    # ¼­¹ö Á¾·á
    if server_socket:
        server_socket.close()
        print("UDP server socket closed")

