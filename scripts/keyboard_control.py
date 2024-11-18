#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from pynput import keyboard
import time
# Initialize the ROS node
rospy.init_node('keyboard_control')

# Create a publisher for the /cmd_vel topic
pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

# Create a Twist message
cmd = Twist()

# Speed values
linear_speed = 1.0
angular_speed = 0.3

# Define key press handler
def on_press(key):
    global cmd
    try:
        if key.char == 'w':
            cmd.linear.x = linear_speed
            cmd.linear.y = 0.0
            cmd.angular.z = 0.0
        elif key.char == 's':
            cmd.linear.x = -linear_speed
            cmd.linear.y = 0.0
            cmd.angular.z = 0.0
        elif key.char == 'a':
            cmd.linear.x = 0.0
            cmd.linear.y = linear_speed
            cmd.angular.z = 0.0
        elif key.char == 'd':
            cmd.linear.x = 0.0
            cmd.linear.y = -linear_speed
            cmd.angular.z = 0.0
        elif key.char == 'q':
            cmd.linear.x = 0.0
            cmd.linear.y = 0.0
            cmd.angular.z = angular_speed
        elif key.char == 'e':
            cmd.linear.x = 0.0
            cmd.linear.y = 0.0
            cmd.angular.z = -angular_speed
        elif key.char == 't':
            cmd.linear.x = 0.1
            cmd.linear.y = 0.0
            cmd.angular.z = 0.0
    except AttributeError:
        pass

# Define key release handler
def on_release(key):
    global cmd
    cmd.linear.x = 0.0
    cmd.linear.y = 0.0
    cmd.angular.z = 0.0
    pub.publish(cmd)

# Main function
if __name__ == '__main__':
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Main loop to publish /cmd_vel
    rate = rospy.Rate(10)  # 10 Hz
    try:
        while not rospy.is_shutdown():
            pub.publish(cmd)
            rate.sleep()
    except rospy.ROSInterruptException:
        pass

