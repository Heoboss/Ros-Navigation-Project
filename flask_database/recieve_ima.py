import mysql.connector
import os

# MySQL 데이터베이스에 연결
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='2024project!',
    database='booksearch'
)

cursor = connection.cursor()

# 특정 bo 값의 이미지 데이터를 가져오기
bo_value = 8
sql = "SELECT image FROM book WHERE bo = %s"
cursor.execute(sql, (bo_value,))

# 쿼리 결과 가져오기
result = cursor.fetchone()
if result and result[0]:
    image_data = result[0]

    # 이미지를 파일로 저장
    with open('retrieved_image.jpg', 'wb') as file:
        file.write(image_data)
    print("이미지가 'retrieved_image.jpg'로 저장되었습니다.")
else:
    print("이미지 데이터가 없습니다.")

cursor.close()
connection.close()
