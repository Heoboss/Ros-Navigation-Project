from gpiozero import DigitalOutputDevice
import sys
import time
import subprocess
import base
import test
from bluetooth import *
import RPi.GPIO as GPIO
import mysql.connector
import os
import signal

# booksearch 데이터베이스에 연결하는 함수
def connect_to_booksearch_db():
    connection = mysql.connector.connect(
        host='192.203.145.54',
        user='pi',
        password='1234',
        database='booksearch'
    )
    return connection

def find_process_id_by_name(process_name):
    p = subprocess.Popen(['pgrep', '-f', process_name], stdout=subprocess.PIPE)
    pid, _ = p.communicate()
    return pid.decode('utf-8').strip().split('\n')

bluetooth_socket = BluetoothSocket(RFCOMM)
bluetooth_socket.connect(("98:DA:60:0B:96:AF", 1))  
print("Bluetooth connected!")


# 명령줄 인자로 전달된 QR 코드 값을 받아옴
if len(sys.argv) > 1:
    value = float(sys.argv[1]) 
    floor = sys.argv[2] # QR 코드로 전달받은 값을 실수로 변환 
    print(f"Received value from go_row: {value}")
else:
    print("No go_row value provided.")
    sys.exit(1)  # 인자가 없으면 프로그램 종료

# 모터 제어용 핀 설정
vaccum = base.pin_num(pin1=20, pin2=21)
actuator = base.pin_num(pin1=23, pin2=24)  # dblack = port3, re = port4

if __name__ == '__main__':
    # QR 코드로부터 받은 값을 각도로 사용
    deg = round(value, 1)
    print("angle:", deg)

    # 서보모터를 지정된 각도로 회전
    test.set_servo_degree(180, speed=5)
    time.sleep(1)
    
    # 모터 제어
    base.motor_control(actuator, direction='forward', speed=1)
    time.sleep(19)

    base.motor_control(vaccum, direction='forward', speed=1)
    time.sleep(1.5)

    base.motor_control(actuator, direction='backward', speed=1)
    time.sleep(21)

    base.motor_stop(actuator)
    time.sleep(0.5)
    base.motor_stop(vaccum)
    
    test.set_servo_degree(0, speed=5)
    time.sleep(2)
    if floor ==  '2':
        booksearch_connection = connect_to_booksearch_db()
        booksearch_cursor = booksearch_connection.cursor()
        booksearch_cursor.execute("UPDATE ros SET go = '3' LIMIT 1;")
        booksearch_connection.commit()
        time.sleep(2)
        bluetooth_socket.send('1')
        print("Bluetooth로 '1' 전송 완료")
        time.sleep(16)
    else:
        print("1 floor") # Bluetooth 데이터 전송 후 대기 시간 설정
        time.sleep(3)
    # ros go 2 
    booksearch_connection = connect_to_booksearch_db()
    booksearch_cursor = booksearch_connection.cursor()
    booksearch_cursor.execute("UPDATE ros SET go = '2' LIMIT 1;")
    booksearch_connection.commit()
    print("Updated 'go' to '2' in ros table.")
    booksearch_cursor.close()
    booksearch_connection.close()
     # ros의 go 값이 '0'으로 돌아갈 때까지 대기
    subprocess.Popen([sys.executable, 'cho.py'])
    
    while True:
        booksearch_connection = connect_to_booksearch_db()
        booksearch_cursor = booksearch_connection.cursor()
        booksearch_cursor.execute("SELECT roca FROM ros LIMIT 1;")
        roca = booksearch_cursor.fetchone()
        if roca[0] == '1':
            break
        elif roca[0] == '0':
            bluetooth_socket.send('2')
            print("lift up")
            time.sleep(24)
            bluetooth_socket.send('1')
            print("lift down")
            time.sleep(16)
            break
            
    while True:
        booksearch_connection = connect_to_booksearch_db()
        booksearch_cursor = booksearch_connection.cursor()
        booksearch_cursor.execute("SELECT * FROM ros LIMIT 1;")
        ros_go_value = booksearch_cursor.fetchone()
        print(ros_go_value)
        # cho.py
        # ros의 'go'가 '0'으로 돌아오면 추가 작업 수행
        if ros_go_value and ros_go_value[0] == '0':
            # pid off
            monitor_pids = find_process_id_by_name('cho.py') #?????? monitor_mysql.py?? pid?? ??????
            for pid in monitor_pids:
                if pid:
                    os.kill(int(pid), signal.SIGTERM) 
                    print("I kill cho")
            bluetooth_socket.send('2')
            print("Bluetooth로 '2' 전송 완료")
            time.sleep(21)
            GPIO.cleanup()
            bluetooth_socket.close()
            # display.py 스크립트를 실행하고 현재 스크립트 종료
            subprocess.Popen([sys.executable, 'fi_display.py'])
            sys.exit()
