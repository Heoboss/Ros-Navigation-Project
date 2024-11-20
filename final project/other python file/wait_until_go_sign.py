import os
import mysql.connector
import time
import subprocess
import signal
import sys

def connect_to_db():
	connection = mysql.connector.connect(
		host='192.203.145.54',
		user='pi',
		password='1234',
		database='booksearch',
		auth_plugin='mysql_native_password'
	)
	return connection

connection = connect_to_db()
cursor = connection.cursor()

while True:
	connection.close()
	connection = connect_to_db()
	cursor = connection.cursor()
	
	cursor.execute("SELECT go FROM ros LIMIT 1;")
	go_row = cursor.fetchone()
	if go_row is not None: 
		print("go_row[0] : " + go_row[0])
		if go_row[0] == '1':
			print("Start ROS System")
			
			# ./run_odom_test.sh ½ÇÇà
			subprocess.Popen(["./run_lidar_odom_test.sh"], shell=True)
			print("run_odom_test.sh executed, waiting for 40 seconds...")
			
			# 40ÃÊ ´ë±â
			time.sleep(25)
			print("다 쉬었다 finished")
			
			# rosrun hector_slam_launch 2dnavgoal.py ½ÇÇà
			subprocess.Popen(["rosrun", "hector_slam_launch", "2dnavgoaltest.py"])
			print("2dnavgoaltest.py executed")
			
			subprocess.Popen(["rosrun", "hector_slam_launch", "make_go_zero.py"])
			print("make_go_zero.py executed")
			connection.close()
			# ÇöÀç ½ºÅ©¸³Æ® Á¾·á
			sys.exit()

