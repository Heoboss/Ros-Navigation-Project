#!/usr/bin/env python3
import rospy
import os
import mysql.connector
import time
import subprocess
import signal
import sys
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Header

def connect_to_db():
    connection = mysql.connector.connect(
        host='192.203.145.54',
        user='pi',
        password='1234',
        database='booksearch',
        auth_plugin='mysql_native_password'
    )
    return connection

def send_goal1():
    rospy.init_node('move_to_goal_nav_goal')

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

    # Set position coordinates based on the target data provided
    goal.pose.position.x = 2.8101418577730595
    goal.pose.position.y = 1.3369631610308845
    goal.pose.position.z = 0.0

    # Set orientation based on the target data provided
    goal.pose.orientation.x = 0.0
    goal.pose.orientation.y = 0.0
    goal.pose.orientation.z = -0.0011395449694230446
    goal.pose.orientation.w = 0.9999993507184205

    # Log the goal coordinates
    rospy.loginfo(f"Sending 2D Nav Goal:\nPosition -> x: {goal.pose.position.x}, y: {goal.pose.position.y}, z: {goal.pose.position.z}\n"
                  f"Orientation -> x: {goal.pose.orientation.x}, y: {goal.pose.orientation.y}, z: {goal.pose.orientation.z}, w: {goal.pose.orientation.w}")

    # Publish the goal
    pub.publish(goal)

    rospy.sleep(1)  # Wait before ending the script


def send_goal2():
    rospy.init_node('move_to_goal_nav_goal')

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

    # Set position coordinates based on the new target data provided
    goal.pose.position.x = 2.835288612930029
    goal.pose.position.y = 1.0324092864877352
    goal.pose.position.z = 0.0

    # Set orientation based on the new target data provided
    goal.pose.orientation.x = 0.0
    goal.pose.orientation.y = 0.0
    goal.pose.orientation.z = 0.007598872063969811
    goal.pose.orientation.w = 0.999971128154886

    # Log the goal coordinates
    rospy.loginfo(f"Sending 2D Nav Goal:\nPosition -> x: {goal.pose.position.x}, y: {goal.pose.position.y}, z: {goal.pose.position.z}\n"
                  f"Orientation -> x: {goal.pose.orientation.x}, y: {goal.pose.orientation.y}, z: {goal.pose.orientation.z}, w: {goal.pose.orientation.w}")

    # Publish the goal
    pub.publish(goal)

    rospy.sleep(1)  # Wait before ending the script


if __name__ == '__main__':
    try:
        # Initialize the ROS node
        rospy.init_node('move_to_goal_nav_goal')

        # Connect to the database
        connection = connect_to_db()
        cursor = connection.cursor()
        
        # Fetch data from the database
        cursor.execute("SELECT * FROM book WHERE name COLLATE utf8mb4_general_ci = 'go';")
        go_row = cursor.fetchone()
        
        # Check go_row value and execute respective goal function
        if go_row and go_row[3] == '1':
            send_goal1()
        elif go_row and go_row[3] == '2':
            send_goal2()

        # Close the database connection
        cursor.close()
        connection.close()

    except rospy.ROSInterruptException:
        pass
    except mysql.connector.Error as err:
        rospy.logerr(f"Database error: {err}")
        if connection.is_connected():
            cursor.close()
            connection.close()

