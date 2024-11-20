#!/usr/bin/env python3
import rospy
import os
import mysql.connector
import time
import subprocess
import signal
import sys
import socket
import threading
from actionlib_msgs.msg import GoalStatusArray
from geometry_msgs.msg import Twist

# UDP ¼ÒÄÏ ¼³Á¤
udp_ip = "0.0.0.0"
udp_port = 50001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))
    
def connect_to_db():
    connection = mysql.connector.connect(
        host='192.203.145.54',
        user='pi',
        password='1234',
        database='booksearch',
        auth_plugin='mysql_native_password'
    )
    return connection

def on_goal_reached():
    # Perform specific actions upon reaching the goal
    rospy.loginfo("Goal reached! Executing post-goal action.")
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE ros SET go = '0' LIMIT 1;")
    connection.commit()
    
    cursor.close()
    connection.close()

    # cmd_vel¿¡ ÀÏ½ÃÀûÀ¸·Î ÀüÁø ¸í·ÉÀ» º¸³¿
    cmd = Twist()
    cmd.linear.x = 1.0
    pub.publish(cmd)
    time.sleep(0.9)
    cmd.linear.x = 0.0
    pub.publish(cmd)

    # move_side ½ºÅ©¸³Æ® ½ÇÇà
    subprocess.Popen(["rosrun", "hector_slam_launch", "move_side.py"])
    print("Start move_side.py")
    subprocess.Popen(["python3", "init_status.py"])
    print("Started init_status.py")
    
    rospy.signal_shutdown("Goal reached, shutting down.")

def goal_status_callback(msg):
    if not msg.status_list:
        return
    latest_status = msg.status_list[-1].status
    if latest_status == 3:  # Status code 3 indicates "Goal reached"
        on_goal_reached()

def udp_listener():
    rospy.loginfo("UDP listener started, waiting for 'w' command...")

    while not rospy.is_shutdown():
        command = '0'
        data, _ = sock.recvfrom(1024)  # ÃÖ´ë 1024¹ÙÀÌÆ® ¼ö½Å
        command = data.decode('utf-8').strip()
        rospy.loginfo("checking w")
        if command == 'W':
            rospy.loginfo("Received 'w' command over UDP.")
            cmd = Twist()
            cmd.linear.x = 1.0  # ¿øÇÏ´Â ¼Óµµ·Î ¼³Á¤
            pub.publish(cmd)
            cmd.linear.x = 0.0
            pub.publish(cmd)

if __name__ == '__main__':
    try:
        rospy.init_node('goal_reached_listener')
        
        # /cmd_vel ÅäÇÈÀ» À§ÇÑ Publisher »ý¼º
        pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Subscribe to the goal status topic to monitor for "goal reached" status
        rospy.Subscriber('/move_base/status', GoalStatusArray, goal_status_callback)

        # UDP listener¸¦ º°µµÀÇ ½º·¹µå·Î ½ÇÇà
        udp_thread = threading.Thread(target=udp_listener)
        udp_thread.daemon = True  # ¸ÞÀÎ ½º·¹µå Á¾·á ½Ã ÇÔ²² Á¾·á
        udp_thread.start()

        # Keep the node running to listen for goal status updates
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
    except socket.error as e:
        rospy.logerr(f"UDP socket error: {e}")
    finally:
        sock.close()  # ÇÁ·Î±×·¥ Á¾·á ½Ã ¼ÒÄÏ ´Ý±â

