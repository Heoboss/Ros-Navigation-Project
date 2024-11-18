import mysql.connector

# MySQL 데이터베이스에 연결
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='2024project!',
    database='booksearch'
)

cursor = connection.cursor()

# 자동 커밋 설정 (필요한 경우)
connection.autocommit = True

# 이미지 파일 읽기
with open('book_ima6.jpg', 'rb') as file:
    binary_data = file.read()

# 특정 bo 값의 행에서 image 열 업데이트
bo_value = 8  # 업데이트하려는 특정 bo 값
sql = "UPDATE book SET image = %s WHERE bo = %s"
cursor.execute(sql, (binary_data, bo_value))

# 커밋 (autocommit이 False인 경우 필요)
connection.commit()

cursor.close()
connection.close()
