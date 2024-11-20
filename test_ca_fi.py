import cv2
from pyzbar import pyzbar
import numpy as np
import time
import mysql.connector
import sys
import subprocess
from bluetooth import *
import socket
import threading
import os

SERVER_IP = '172.20.10.4'  
PORT = 65432

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
go_thread = True  

def move():
    global go_thread
    
    while go_thread:  
        message = "1"
        client_socket.sendto(message.encode(), (SERVER_IP, PORT))
        time.sleep(0.17)
        message = "0"
        client_socket.sendto(message.encode(), (SERVER_IP, PORT))
        time.sleep(3)
    print("Move thread stopped.")


def start_move_thread():
    move_thread = threading.Thread(target=move)
    move_thread.start()
    return move_thread
    




# booksearch 데이터베이스에 연결하는 함수
def connect_to_booksearch_db():
    connection = mysql.connector.connect(
        host='192.203.145.54',
        user='pi',
        password='1234',
        database='booksearch'
    )
    return connection


# Bluetooth 초기 설정
if len(sys.argv) > 1:
    go_row_value = sys.argv[1]  # QR 코드 값
    go_floor_value = sys.argv[2]  # floor 값
    print(go_floor_value)
    print(f"Received value from go_row: {go_row_value}")
else:
    print("No go_row value provided.")
    sys.exit(1)  # 인자가 없으면 종료

# Bluetooth 연결 (예시로 주석 처리)
socket = BluetoothSocket(RFCOMM)
socket.connect(("98:DA:60:0B:96:AF", 1))  # Bluetooth 주소
print("bluetooth connected!")
msg = go_floor_value.strip()
socket.send(msg)
if msg == "2":
    time.sleep(21)
booksearch_connection = connect_to_booksearch_db()
booksearch_cursor = booksearch_connection.cursor()

# QR 코드의 회전 각도 계산 함수
def calculate_rotation_angle_using_finder_patterns(polygon):
    if len(polygon) == 4:
        points = [(point.x, point.y) for point in polygon]
        points = sorted(points, key=lambda point: point[0])
        top_left = min(points[:2], key=lambda point: point[1])
        top_right = min(points[2:], key=lambda point: point[1])

        dx = top_right[0] - top_left[0]
        dy = top_right[1] - top_left[1]
        angle = np.degrees(np.arctan2(dy, dx))
        return angle
    return 0

# QR 코드가 중앙 사각형의 중심으로부터 일정 범위 내에 있는지 확인하는 함수
def is_qr_center_within_region(qr_center_x, qr_center_y, center_x, center_y, region_size=1):
    return center_x - region_size <= qr_center_x <= center_x + region_size 

# QR 코드를 중앙 사각형 내에서 처리하는 함수
def detect_qr_code_in_blue_box(cap, go_row_value, region_size=100):
    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 가져올 수 없습니다.")
            break

        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2  # 프레임의 중앙 좌표

        # 중앙 사각형의 좌표 설정 (예시: 200x200 크기의 중앙 사각형)
        x1, y1 = center_x - region_size//2 + 1, center_y - region_size - 150
        x2, y2 = center_x + region_size//2 + 1 , center_y + region_size + 150
        
        # 중앙 사각형 그리기
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # 파란색 사각형
        # QR 코드 디코딩
        qr_codes = pyzbar.decode(frame)
        if not qr_codes:
            print("QR 코드를 찾을 수 없습니다.")
            #side code moving
            #move()
            print(" not find QR ")
            #cv2.imshow('Processed Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        for qr_code in qr_codes:
            # QR 코드의 위치 정보
            x, y, w, h = qr_code.rect
            qr_center_x = x + w // 2  # QR 코드 중심 x좌표
            qr_center_y = y + h // 2  # QR 코드 중심 y좌표

            # QR 코드가 중앙 사각형 안에 있는지 확인
            if x1 <= x <= x2 and y1-100 <= y <= y2+100 and x1 <= x + w <= x2 and y1 - 100 <= y + h <= y2 + 100:
                # QR 코드의 중심이 중앙값(region_size) 내에 있을 때만 처리
                if is_qr_center_within_region(qr_center_x, qr_center_y, center_x, center_y, region_size):
                    qr_data = qr_code.data.decode('utf-8')
                    qr_type = qr_code.type
                    print(f"QR 코드가 중앙 사각형 안에 있습니다: {qr_data}")
                    # QR 코드 정보와 테두리 표시
                    text = f"{qr_data} ({qr_type})"
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 녹색 사각형으로 QR 코드 테두리 표시
                    # QR 코드가 목표 코드인지 확인 후 'S' 신호 송신
                    if str(qr_data).strip() == str(go_row_value).strip():
                        print(f"목표 QR 코드 {go_row_value} 탐지됨. '0' 신호 송신.")
                        '''side code find'''
                        message = "2"  
                        client_socket.sendto(message.encode(), (SERVER_IP, PORT))
                        print("Socket QR find")
                        go_thread = False
                      #  move_thread.join()
                        # QR 코드가 중앙에 맞춰지도록 보상 시스템 수행 (프레임을 계속 갱신)
                        #frame = center_qr_code(cap, qr_code, center_x)
                            
                        # QR 코드의 회전 각도 계산
                        polygon = qr_code.polygon
                        angle = calculate_rotation_angle_using_finder_patterns(polygon)
                        print(f"QR 코드 회전 각도: {angle}°")
                        
                        
                        # 모터 제어 스크립트 실행
                        cap.release()
                        cv2.destroyAllWindows()
                        socket.close()
                        subprocess.Popen([sys.executable, 'motor2.py', str(angle),go_floor_value ])
                        os._exit(0)
                    else:
                        print(f"QR 코드 {qr_data}는 목표 코드가 아닙니다. 계속 탐색 중...")
                        ''' side code moving'''
                        #move()
                        print("socket not match QR")
            else:
                '''side code moving'''
                #move()
                print("socket not box")

        # 업데이트된 프레임을 표시
        #cv2.imshow('Processed Frame', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return

# 카메라 시작
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

try:
    # QR 코드 탐지 및 중앙 사각형 안에서만 처리
    move_thread = start_move_thread()
    detect_qr_code_in_blue_box(cap, go_row_value, region_size=100)
finally:
    cap.release()
    cv2.destroyAllWindows()

