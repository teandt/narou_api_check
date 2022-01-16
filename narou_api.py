import json
import requests
import gzip
import pymysql.cursors
import datetime


url = "http://api.syosetu.com/novelapi/api/"

payload = {"out": "json", "gzip": "5", "order": "old", "lim": "10"}

res = requests.get(url, params=payload)
cont = gzip.decompress(res.content).decode("utf-8")

res_json = json.loads(cont)

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
            result = cursor.fetchone()            
    except:
        db.close()
    else:
        db.close()
    
    return result["parameter_value"]


cnt = check_count()
timestamp = datetime.datetime.now().isoformat(timespec='seconds')

try:
    db = db_connect()
    with db.cursor() as cursor:
        for i in res_json:
            if("ncode" in i):
                sql = "INSERT INTO contents_tbl SET count = %s, ncode = %s, title = %s"
                cursor.execute(sql, (cnt + 1, i["ncode"], i["title"]))
        
        sql = "UPDATE parameter_tbl SET parameter_value = %s WHERE parameter_name = 'counter'"
        cursor.execute(sql, (cnt + 1))

        sql = "INSERT INTO count_timestamp_tbl SET count = %s, timestamp = %s"
        cursor.execute(sql, (cnt + 1, timestamp))
except:
    print("error rollback")
    db.rollback()
    db.close()
else:
    db.commit()
    db.close()


# try:
#     db = db_connect()
#     with db.cursor() as cursor:
#         sql = "SELECT title FROM contents_tbl WHERE count=%s"
#         cursor.execute(sql,(cnt))
#         result = cursor.fetchall()
#         for i in result:
#             print(i["title"])
# except:
#     db.close()
# else:
#     db.close()
