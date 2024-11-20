#!/usr/bin/env python3
import rospy, tf, tf2_ros, geometry_msgs.msg, nav_msgs.msg
# This node is the work of https://github.com/ne0h/hmmwv/blob/hmmwv2/ros_workspace/src/hmmwv/nodes/odomtransformer.py 

def callback(data, args):
	bc = tf2_ros.TransformBroadcaster()
	t = geometry_msgs.msg.TransformStamped()
	
	t.header.stamp = rospy.Time.now()
	t.header.frame_id = args[0]
	t.child_frame_id = args[1]
	
	t.transform.translation = data.pose.pose.position
	t.transform.rotation = data.pose.pose.orientation
	bc.sendTransform(t)
	# bc.sendTransform((data.pose.pose.position.x, data.pose.pose.position.y, 0) , (data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z, data.pose.pose.orientation.w), rospy.Time.now(), args[1], args[0])

if __name__ == "__main__":
	rospy.init_node("odomtransformer")
	odomInput = rospy.get_param("~odom_input")
	tfOutput  = rospy.get_param("~tf_output")
	rospy.Subscriber(odomInput, nav_msgs.msg.Odometry, callback, [odomInput, tfOutput])
	rospy.spin()
	
"""#!/usr/bin/env python3
import rospy
import tf2_ros
import geometry_msgs.msg
import nav_msgs.msg
import tf.transformations as transformations  # For quaternion operations

def callback(data, args):
    bc = tf2_ros.TransformBroadcaster()
    t = geometry_msgs.msg.TransformStamped()
    
    t.header.stamp = rospy.Time.now()
    t.header.frame_id = args[0]  # odom_input (scanmatch_odom)
    t.child_frame_id = args[1]   # tf_output (base_link)

    # Set the position from odometry data (no modification needed for position)
    t.transform.translation = data.pose.pose.position
    
    # Convert the incoming orientation to a quaternion (scanmatch_odom orientation)
    original_orientation = [
        data.pose.pose.orientation.x,
        data.pose.pose.orientation.y,
        data.pose.pose.orientation.z,
        data.pose.pose.orientation.w
    ]
    
    # Define a 180-degree rotation around the z-axis (yaw)
    yaw_rotation = 180 * (3.14159265359 / 180)  # Convert degrees to radians (¥ð radians)
    
    # Create a quaternion representing this 180-degree rotation
    rotation_quaternion = transformations.quaternion_from_euler(0, 0, yaw_rotation)
    
    # Apply only the 180-degree rotation to the base_link frame
    rotated_orientation = transformations.quaternion_multiply(rotation_quaternion, [0, 0, 0, 1])
    
    # Set the orientation with the 180-degree rotation applied
    t.transform.rotation.x = rotated_orientation[0]
    t.transform.rotation.y = rotated_orientation[1]
    t.transform.rotation.z = rotated_orientation[2]
    t.transform.rotation.w = rotated_orientation[3]

    # Broadcast the transform (base_link with 180-degree rotation)
    bc.sendTransform(t)

if __name__ == "__main__":
    rospy.init_node("odomtransformer")
    odomInput = rospy.get_param("~odom_input")  # e.g., "/scanmatch_odom"
    tfOutput  = rospy.get_param("~tf_output")   # e.g., "/base_link"
    
    # Subscribe to the scanmatch_odom topic
    rospy.Subscriber(odomInput, nav_msgs.msg.Odometry, callback, [odomInput, tfOutput])
    
    rospy.spin()
    """



