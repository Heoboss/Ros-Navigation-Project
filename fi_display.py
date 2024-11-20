import socketio
import speech_recognition as sr
import os
import mysql.connector
import subprocess
import time
import sys
from bluetooth import BluetoothSocket, RFCOMM
import signal

# SocketIO 클라이언트 생성 및 Bluetooth 연결 설정
sio = socketio.Client()
bluetooth_socket = BluetoothSocket(RFCOMM)
bluetooth_socket.connect(("98:DA:60:0B:96:AF", 1))  
print("Bluetooth connected!")

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

@sio.event
def connect():
    print('서버에 연결되었습니다.')

@sio.event
def disconnect():
    print('서버에서 연결이 끊어졌습니다.')

# 음성 인식을 시작하는 이벤트 핸들러
@sio.on('start_voice_recognition', namespace='/raspberry')
def start_voice_recognition():
    print('음성 인식을 시작합니다..')
    
    # 음성 인식 시작 알림을 서버에 전송
    sio.emit('listening_started', namespace='/raspberry')

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("소음 조정 중..")
        recognizer.adjust_for_ambient_noise(source)
        print("말씀해 주세요...")
        
        audio = recognizer.listen(source)
    
    try:
        recognized_text = recognizer.recognize_google(audio, language='ko-KR')
        print(f"인식된 텍스트: {recognized_text}")
    except sr.UnknownValueError:
        recognized_text = '음성을 인식하지 못했습니다.'
    except sr.RequestError as e:
        recognized_text = f"음성 인식 서비스에 오류가 발생했습니다; {e}"
    
    # 인식 결과를 서버에 전송
    sio.emit('voice_result', {'recognized_text': recognized_text}, namespace='/raspberry')
    
    # 음성 인식 종료 알림을 서버에 전송
    sio.emit('voice_recognition_ended', namespace='/raspberry')

def check_database_and_run_process():
    booksearch_connection = connect_to_booksearch_db()
    booksearch_cursor = booksearch_connection.cursor()

    try:
        # booksearch 데이터베이스 초기화
        booksearch_cursor.execute("UPDATE book SET barcode = '000', floor = '0' WHERE name COLLATE utf8mb4_general_ci = 'go';")
        booksearch_connection.commit()
        print("Initialized 'barcode' to '000' and 'floor' to '0' for 'go' row in book table.")
    except mysql.connector.Error as e:
        print(f"Database error during initialization: {e}")
    finally:
        booksearch_cursor.close()
        booksearch_connection.close()

    # 데이터베이스 모니터링 루프
    while True:
        # booksearch 데이터베이스에서 'go' 행 조회
        booksearch_connection = connect_to_booksearch_db()
        booksearch_cursor = booksearch_connection.cursor()
        booksearch_cursor.execute("SELECT * FROM book WHERE name COLLATE utf8mb4_general_ci = 'go';")
        go_row = booksearch_cursor.fetchone()
        
        if go_row is not None and go_row[1] != '000':
            bluetooth_socket.send('1')
            print("Bluetooth로 '1' 전송 완료")
            time.sleep(2)  # Bluetooth 데이터 전송 후 대기 시간 설정
            booksearch_cursor.execute("UPDATE ros SET go = '1' LIMIT 1;")
            booksearch_connection.commit()
            print("Updated 'go' to '1' in ros table.")
            booksearch_cursor.close()
            booksearch_connection.close()
            time.sleep(14)
            subprocess.Popen([sys.executable, 'cho.py'])
            # ros의 go 값이 '0'으로 돌아갈 때까지 대기
            while True:
                booksearch_connection = connect_to_booksearch_db()
                booksearch_cursor = booksearch_connection.cursor()
                booksearch_cursor.execute("SELECT * FROM ros LIMIT 1;")
                ros_go_value = booksearch_cursor.fetchone()
                print(ros_go_value)
                # ros의 'go'가 '0'으로 돌아오면 추가 작업 수행
                if ros_go_value and ros_go_value[0] == '0':
                    monitor_pids = find_process_id_by_name('cho.py')
                    for pid in monitor_pids:
                        if pid:
                            os.kill(int(pid), signal.SIGTERM) 
                            print("I kill cho")
                    print("ros 테이블 'go'의 값이 '0'으로 변경되었습니다. 추가 작업을 실행합니다.")
                    bluetooth_socket.close()
                    subprocess.Popen([sys.executable, 'test_ca_fi.py', go_row[1], go_row[6]])
                    time.sleep(1)
                    sys.exit(0)
                    break

                # 일정 시간 대기 후 다시 확인
                time.sleep(5)

        booksearch_cursor.close()
        booksearch_connection.close()

    # 연결 닫기
    bluetooth_socket.close()  # Bluetooth 소켓 닫기

if __name__ == '__main__':
    # 서버에 연결
    sio.connect('http://192.203.145.54:5000/raspberry')

    # 데이터베이스 확인 함수 실행
    check_database_and_run_process()

    # 소켓 이벤트 대기
    sio.wait()

    # 스크립트 종료
    os._exit()
