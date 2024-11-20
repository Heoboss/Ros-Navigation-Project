#!/usr/bin/env python3
import rospy
from actionlib_msgs.msg import GoalID
from move_base_msgs.msg import MoveBaseActionGoal
import time

# ROS ³ëµå ÃÊ±âÈ­
rospy.init_node('temporary_goal_setter')

# ÆÛºí¸®¼Å »ý¼º
goal_pub = rospy.Publisher('/move_base/goal', MoveBaseActionGoal, queue_size=1)
cancel_pub = rospy.Publisher('/move_base/cancel', GoalID, queue_size=1)

# Àá½Ã ´ë±âÇÏ¿© ÆÛºí¸®¼Å°¡ ÁØºñµÉ ¶§±îÁö ±â´Ù¸²
time.sleep(1)

# ÀÓ½Ã ¸ñÇ¥ »ý¼º ¹× Àü¼Û
goal = MoveBaseActionGoal()
goal.goal_id.stamp = rospy.Time.now()
goal.goal.target_pose.header.frame_id = "map"
goal.goal.target_pose.pose.position.x = 0.0
goal.goal.target_pose.pose.position.y = 0.0
goal.goal.target_pose.pose.orientation.w = 1.0
goal_pub.publish(goal)

# Àá½Ã ´ë±â ÈÄ ¸ñÇ¥ Ãë¼Ò
time.sleep(0.1)
cancel_pub.publish(GoalID())  # ÀÓ½Ã ¸ñÇ¥¸¦ Áï½Ã Ãë¼Ò

print("Temporary goal sent and canceled.")

