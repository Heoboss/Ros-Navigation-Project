from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
import mysql.connector
from mysql.connector import Error
from datetime import date
import requests
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2024project!',
            database='booksearch',
            autocommit=True
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('query')
    view_type = request.form.get('view_type', 'list')  # 기본 값은 'list'
    connection = get_db_connection()
    if connection is None:
        return render_template('index.html', error="Database connection failed.")
    
    cursor = connection.cursor()

    try:
        query = "SELECT name, barcode, bookshelf, here, image FROM book WHERE name COLLATE utf8mb4_general_ci LIKE %s"
        cursor.execute(query, ('%' + search_term + '%',))
        results = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
        results = []
    finally:
        cursor.close()
        connection.close()
    
    return render_template('index.html', results=results, query=search_term, view_type=view_type)

@app.route('/check_book_status', methods=['POST'])
def check_book_status():
    data = request.get_json()
    name = data.get('name')
    barcode = data.get('barcode')

    connection = get_db_connection()
    if connection is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    cursor = connection.cursor()

    try:
        query = "SELECT here FROM book WHERE name COLLATE utf8mb4_general_ci = %s AND barcode = %s"
        cursor.execute(query, (name, barcode))
        result = cursor.fetchone()
        cursor.fetchall()  # Fetch all remaining results to avoid unread result error
        if result:
            status = result[0]
            print(f"Book status for {name} with barcode {barcode}: {status}")
            return jsonify({'status': status})
        else:
            print(f"Book not found: {name} with barcode {barcode}")
            return jsonify({'status': 'error', 'message': 'Book not found.'}), 404
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/update_go', methods=['POST'])
def update_go():
    data = request.get_json()
    current_book_name = data.get('name')
    current_book_barcode = data.get('barcode')
    connection = get_db_connection()
    if connection is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
    
    cursor = connection.cursor()

    try:
        select_query = "SELECT barcode, bookshelf, floor FROM book WHERE name COLLATE utf8mb4_general_ci = %s AND barcode = %s"
        cursor.execute(select_query, (current_book_name, current_book_barcode))
        current_book = cursor.fetchone()
    
        if current_book:
            barcode, bookshelf, floor = current_book
            update_query = "UPDATE book SET barcode = %s, bookshelf = %s, floor = %s WHERE name = 'go'"
            cursor.execute(update_query, (barcode, bookshelf, floor))
        else:
            return jsonify({'status': 'error', 'message': 'Book not found.'}), 404
    except Error as e:
        print(f"Error: {e}")
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'status': 'success'})

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search_term = request.args.get('query')
    connection = get_db_connection()
    if connection is None:
        return jsonify([]), 500
    
    cursor = connection.cursor()
    try:
        query = "SELECT name FROM book WHERE name COLLATE utf8mb4_general_ci LIKE %s LIMIT 10"
        cursor.execute(query, ('%' + search_term + '%',))
        results = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
        results = []
    finally:
        cursor.close()
        connection.close()
    
    names = [row[0] for row in results]
    return jsonify(names)

@app.route('/validate_login', methods=['POST'])
def validate_login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')
    book_name = data.get('book_name')
    book_barcode = data.get('book_barcode')

    connection = get_db_connection()
    if connection is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
    
    cursor = connection.cursor()

    try:
        query = "SELECT borrowed_books FROM userdatabase WHERE user_id = %s AND password = %s"
        cursor.execute(query, (user_id, password))
        result = cursor.fetchone()
        cursor.fetchall()  # Fetch all remaining results to avoid unread result error
        
        if result:
            borrowed_books = result[0]
            if borrowed_books >= 5:
                response = {'status': 'exceed'}
            else:
                update_query = "UPDATE userdatabase SET borrowed_books = borrowed_books + 1 WHERE user_id = %s"
                cursor.execute(update_query, (user_id,))
                connection.commit()
                response = {'status': 'success', 'borrowed_books': borrowed_books + 1}
                insert_borrowed_book(user_id, book_name, book_barcode)
        else:
            response = {'status': 'failure'}
    except Error as e:
        print(f"Error: {e}")
        response = {'status': 'error', 'message': str(e)}
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    
    return jsonify(response)

def insert_borrowed_book(user_id, book_name, book_barcode):
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed.")
        return
    
    cursor = connection.cursor()
    try:
        insert_query = "INSERT INTO borrowed_books (user_id, book_title, borrowed_date) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (user_id, book_name, date.today()))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

@app.route('/update_book_here', methods=['POST'])
def update_book_here():
    data = request.get_json()
    book_name = data.get('book_name')
    book_barcode = data.get('book_barcode')
    status = data.get('status')

    connection = get_db_connection()
    if connection is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
    
    cursor = connection.cursor()

    try:
        update_query = "UPDATE book SET here = %s WHERE name COLLATE utf8mb4_general_ci = %s AND barcode = %s"
        cursor.execute(update_query, (status, book_name, book_barcode))
        connection.commit()
        response = {'status': 'success'}
    except Error as e:
        print(f"Error: {e}")
        response = {'status': 'error', 'message': str(e)}
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    
    return jsonify(response)

@app.route('/seating_chart')
def seating_chart():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
    
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM seats")
        seats = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
        seats = []
    finally:
        cursor.close()
        connection.close()
    
    return jsonify(seats)

@app.route('/update_seat', methods=['POST'])
def update_seat():
    data = request.get_json()
    seat_id = data.get('seat_id')
    new_status = data.get('status')
    book_name = data.get('book_name')
    book_barcode = data.get('book_barcode')

    connection = get_db_connection()
    if connection is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    cursor = connection.cursor()

    try:
        update_seat_query = "UPDATE seats SET status = %s WHERE seat_id = %s"
        cursor.execute(update_seat_query, (new_status, seat_id))
        
        update_book_query = "UPDATE book SET here = '대출불가능합니다.' WHERE name COLLATE utf8mb4_general_ci = %s AND barcode = %s"
        cursor.execute(update_book_query, (book_name, book_barcode))

        connection.commit()
        response = {'status': 'success'}
    except Error as e:
        print(f"Error: {e}")
        response = {'status': 'error', 'message': str(e)}
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    
    return jsonify(response)
@socketio.on('voice_recognition')
def handle_voice_request(data):
    print('음성 인식 요청을 받았습니다. 라즈베리파이에 요청을 전달합니다.')
    # 클라이언트에게 음성 인식이 시작되었음을 알림
    socketio.emit('start_voice_recognition')
    # 라즈베리파이에 음성 인식 요청 이벤트 전송
    socketio.emit('start_voice_recognition', namespace='/raspberry')

# 라즈베리파이에서 음성 인식이 실제로 시작될 때 (환경 소음 조정 후)
@socketio.on('listening_started', namespace='/raspberry')
def handle_listening_started():
    print('음성 인식이 시작되었습니다...')
    socketio.emit('listening_started')  # 클라이언트에게 음성 인식 중임을 알림

# 라즈베리파이로부터 음성 인식 결과 수신
@socketio.on('voice_result', namespace='/raspberry')
def handle_voice_result(data):
    recognized_text = data.get('recognized_text', '')
    print(f'라즈베리파이로부터 음성 인식 결과를 받았습니다: {recognized_text}')
    # 클라이언트에게 음성 인식 결과를 전송하고 음성 인식이 종료되었음을 알림
    socketio.emit('voice_response', {'message': recognized_text})
    
@app.route('/update_roca', methods=['POST'])
def update_roca():
    data = request.get_json()
    new_value = data.get('value')  # 1 또는 2 값을 받음

    connection = get_db_connection()
    if connection is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    cursor = connection.cursor()
    try:
        # ros 테이블의 roca 값을 업데이트
        update_query = "UPDATE ros SET roca = %s WHERE go = 0 AND side = 0"
        cursor.execute(update_query, (new_value,))
        connection.commit()
        return jsonify({'status': 'success', 'message': f'roca updated to {new_value}'})
    except Error as e:
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)