import pymysql.cursors
import datetime


def db_connect():
    db = pymysql.connect(host='127.0.0.1',
                        port=23306,
                        user='narouDB',
                        password='narouDB',
                        database='narou_db',
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)
    return db

def check_count():
    db = db_connect()

    try:
        with db.cursor() as cursor:
            sql = "SELECT parameter_value  FROM parameter_tbl WHERE parameter_name='counter'"
            cursor.execute(sql)
            data = cursor.fetchone()
            if data == None:
                print("counter value data is none")
                return -1
            else:
                result = data
    finally:
        db.close()
    
    return result["parameter_value"]


cnt = check_count()
if cnt >= 0:
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
else:
    print("error cnt value")
    exit()

try:
    db = db_connect()
    with db.cursor() as cursor:
        sql = "SELECT * FROM contents_tbl WHERE count=%s"
        cursor.execute(sql,(cnt))
        result = cursor.fetchall()
        for i in result:
            print(i)
finally:
    db.close()