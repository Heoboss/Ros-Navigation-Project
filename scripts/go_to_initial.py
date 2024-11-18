#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import Header
from actionlib_msgs.msg import GoalStatusArray
import mysql.connector
import subprocess
import sys
import time
import socket
import threading

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

    subprocess.Popen(["python3", "init_status.py"])
    print("Started init_status.py")
    
    # Terminate ROS-related processes
    subprocess.Popen("ps aux | grep ros | grep -v grep | awk '{print $2}' | xargs -r kill -9", shell=True)
    print("Terminated ROS-related processes.")

    # Start wait_until_go_sign.py
    subprocess.Popen(["python3", "wait_until_go_sign.py"])
    print("Started wait_until_go_sign.py")
    
    rospy.signal_shutdown("Goal reached, shutting down.")

def goal_status_callback(msg):
    if not msg.status_list:
        return
    latest_status = msg.status_list[-1].status
    if latest_status == 3:  # Status code 3 indicates "Goal reached"
        on_goal_reached()

def send_goal():
    # Publisher for move_base_simple/goal topic
    pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)

    # Wait for the publisher to connect
    rospy.sleep(1)

    # Create a PoseStamped message
    goal = PoseStamped()

    # Header information
    goal.header = Header()
    goal.header.stamp = rospy.Time.now()
    goal.header.frame_id = "map"  # Specify the frame as "map"

    # Set position coordinates from the provided values
    goal.pose.position.x = 0.015616314569546298
    goal.pose.position.y = 0.005075619171704649
    goal.pose.position.z = 0.0

    # Set orientation
    goal.pose.orientation.x = 0.0
    goal.pose.orientation.y = 0.0
    goal.pose.orientation.z = 0.00021554621661461633
    goal.pose.orientation.w = 0.999999976769914

    # Log the goal coordinates
    rospy.loginfo(f"Sending 2D Nav Goal:\nPosition -> x: {goal.pose.position.x}, y: {goal.pose.position.y}, z: {goal.pose.position.z}\n"
                  f"Orientation -> x: {goal.pose.orientation.x}, y: {goal.pose.orientation.y}, z: {goal.pose.orientation.z}, w: {goal.pose.orientation.w}")

    # Publish the goal
    pub.publish(goal)

def udp_listener():
    # UDP ¼ÒÄÏ ¼³Á¤
    udp_ip = "0.0.0.0"
    udp_port = 50001
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))

    rospy.loginfo("UDP listener started, waiting for 'w' command...")

    # Publisher for cmd_vel topic
    pub_cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    while not rospy.is_shutdown():
        command = '0'
        data, _ = sock.recvfrom(1024)  # ÃÖ´ë 1024¹ÙÀÌÆ® ¼ö½Å
        command = data.decode('utf-8').strip()
        rospy.loginfo("checking for 'w' command")
        if command == 'W':
            rospy.loginfo("Received 'w' command over UDP.")
            cmd = Twist()
            cmd.linear.x = 1.0  # ¿øÇÏ´Â ¼Óµµ·Î ¼³Á¤
            pub_cmd_vel.publish(cmd)
            cmd.linear.x = 0.0
            pub_cmd_vel.publish(cmd)

if __name__ == '__main__':
    try:
        # Initialize the ROS node
        rospy.init_node('move_to_goal_nav_goal')

        # Subscribe to the goal status topic to monitor for "goal reached" status
        rospy.Subscriber('/move_base/status', GoalStatusArray, goal_status_callback)

        send_goal()
        
        # Start UDP listener in a separate thread
        udp_thread = threading.Thread(target=udp_listener)
        udp_thread.daemon = True  # ¸ÞÀÎ ½º·¹µå Á¾·á ½Ã ÇÔ²² Á¾·á
        udp_thread.start()

        # Keep the node running to listen for goal status updates
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
    except socket.error as e:
        rospy.logerr(f"UDP socket error: {e}")

