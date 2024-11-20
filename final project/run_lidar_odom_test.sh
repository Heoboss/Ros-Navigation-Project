#!/bin/bash

# 1. roscore ½ÇÇà
roscore &
# roscore°¡ ¹é±×¶ó¿îµå¿¡¼­ ½ÇÇàµÇµµ·Ï ÇÔ

# 2. 5ÃÊ ±â´Ù¸² (roscore°¡ ¿ÏÀüÈ÷ ½ÇÇàµÇµµ·Ï)
sleep 5

# 3. hector_slam odomtransformer.launch ½ÇÇà
roslaunch hector_slam_launch odomtransformer.launch &
# ¹é±×¶ó¿îµå¿¡¼­ ½ÇÇà
sleep 5
# 4. rplidar A1 ½ÇÇà
roslaunch rplidar_ros rplidar_a1.launch &
# ¹é±×¶ó¿îµå¿¡¼­ ½ÇÇà

# 5. 5ÃÊ ±â´Ù¸²
sleep 5

# 6. odom_test.launch ½ÇÇà
roslaunch hector_slam_launch odom_test.launch
#roslaunch hector_slam_launch tutorial.launch
