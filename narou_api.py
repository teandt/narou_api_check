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
if cnt > 0:
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
else:
    print("error cnt value")
    exit()

try:
    db = db_connect()
    with db.cursor() as cursor:
        for i in res_json:
            if("ncode" in i):
                sql = "INSERT INTO contents_tbl SET count = %s, ncode = %s, title = %s, userid = %s, writer = %s, story = %s, biggenre = %s, genre = %s, \
                      gensaku = %s, keyword = %s, general_firstup = %s, general_lastup = %s, novel_type = %s, end = %s, general_all_no = %s, \
                      length = %s, time = %s, isstop = %s, isr15 = %s"
                cursor.execute(sql, (cnt + 1, i["ncode"], i["title"], i["userid"], i["writer"], i["story"], i["biggenre"], i["genre"],\
                                     i["gensaku"], i["keyword"], i["general_firstup"], i["general_lastup"], i["novel_type"], i["end"], i["general_all_no"], \
                                     i["length"], i["time"], i["isstop"], i["isr15"]))
        
        sql = "UPDATE parameter_tbl SET parameter_value = %s WHERE parameter_name = 'counter'"
        cursor.execute(sql, (cnt + 1))

        sql = "INSERT INTO count_timestamp_tbl SET count = %s, timestamp = %s"
        cursor.execute(sql, (cnt + 1, timestamp))
except:
    print("error rollback")
    db.rollback()
else:
    db.commit()
finally:
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
