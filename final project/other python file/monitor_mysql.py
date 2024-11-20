import os
import mysql.connector
import serial
import time
import math
import subprocess
import signal
import math
import sys
# 종료할 파이썬 파일의 PID를 찾는 함수
def find_process_id_by_name(process_name):
    p = subprocess.Popen(['pgrep', '-f', process_name], stdout=subprocess.PIPE)
    pid, _ = p.communicate()
    return pid.strip()
def connect_to_db():
	connection = mysql.connector.connect(
		host='192.203.145.54',
		user='pi',
		password='1234',
		database='booksearch'
	)
	return connection
connection = connect_to_db()
cursor = connection.cursor()
#cursor.execute("SELECT * FROM booksearch.book;")
"""cursor.execute("SELECT * FROM booksearch.book WHERE name COLLATE utf8mb4_general_ci = 'go';")
go_row=cursor.fetchone()
print(go_row[2]=='1')"""
while True:
	
	connection.close()
	connection = connect_to_db()
	cursor=connection.cursor()
	
	cursor.execute("SELECT * FROM booksearch.book WHERE name COLLATE utf8mb4_general_ci = 'go';")
	go_row = cursor.fetchone()
	if go_row is not None: 
		print("go_row[2] : "+go_row[2])
		if go_row[2]!='0':
			subprocess.Popen([sys.executable, '/home/pi/joljak/move_motor.py'])
			time.sleep(1)
			break
	
cursor.close()
connection.close()
