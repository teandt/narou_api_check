import json
import requests
import gzip
import datetime
import pymysql.cursors
import datetime
import time

url = "http://api.syosetu.com/novelapi/api/"

def get_allcount():
    payload = {"out": "json", "gzip": "5","lim": "1"}

    retry = 0
    while retry < 5:
        try:
            res = requests.get(url, params=payload)
            break
        except:
            print("connection error: not get allcount")
            retry = retry + 1
            time.sleep(10)

    cont = gzip.decompress(res.content).decode("utf-8")
    res_json = json.loads(cont)
    allcount = int(res_json[0]["allcount"])

    return allcount

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


# ========================================================================================================================== #
if __name__ == "__main__":

    lastup = int(datetime.datetime.now().timestamp())
    #allcount = get_allcount()

    try:
        with open("temp.json", "r") as f:
            data = json.load(f)
    except:
        print("error not open file")
        exit()

    cnt = check_count()
    if cnt >= 0:
        timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    else:
        print("error cnt value")
        exit()

    try:
        db = db_connect()
        chk = []
        with db.cursor() as cursor:
            sql = "UPDATE parameter_tbl SET parameter_value = %s WHERE parameter_name = 'counter'"
            cursor.execute(sql, (cnt + 1))

            sql = "INSERT INTO count_timestamp_tbl SET count = %s, timestamp = %s"
            cursor.execute(sql, (cnt + 1, timestamp))

            #sql = "INSERT INTO count_allcount_tbl SET count = %s, allcount = %s"
            #cursor.execute(sql, (cnt + 1, allcount))

            for i in data:
                chk = i
                if("ncode" in i):
                    sql = "INSERT INTO contents_tbl SET count = %s, ncode = %s, title = %s, userid = %s, writer = %s, story = %s, biggenre = %s, genre = %s, \
                        gensaku = %s, keyword = %s, general_firstup = %s, general_lastup = %s, novel_type = %s, end = %s, general_all_no = %s, \
                        length = %s, time = %s, isstop = %s, isr15 = %s, isbl = %s, isgl = %s, iszankoku = %s, istensei = %s, istenni = %s, \
                        pc_or_k = %s, global_point = %s, daily_point = %s, weekly_point = %s, monthly_point = %s, \
                        quarter_point = %s, yearly_point = %s, fav_novel_cnt = %s, impression_cnt = %s, review_cnt = %s, all_point = %s, \
                        all_hyoka_cnt = %s, sasie_cnt = %s, kaiwaritu = %s, novelupdated_at = %s, updated_at = %s"
                    cursor.execute(sql, (cnt + 1, i["ncode"], i["title"], i["userid"], i["writer"], i["story"], i["biggenre"], i["genre"],\
                                        i["gensaku"], i["keyword"], i["general_firstup"], i["general_lastup"], i["novel_type"], i["end"], i["general_all_no"], \
                                        i["length"], i["time"], i["isstop"], i["isr15"], i["isbl"], i["isgl"], i["iszankoku"], i["istensei"], i["istenni"], \
                                        i["pc_or_k"], i["global_point"], i["daily_point"], i["weekly_point"], i["monthly_point"], \
                                        i["quarter_point"], i["yearly_point"], i["fav_novel_cnt"], i["impression_cnt"], i["review_cnt"], i["all_point"], \
                                        i["all_hyoka_cnt"], i["sasie_cnt"], i["kaiwaritu"], i["novelupdated_at"], i["updated_at"]))
    except:
        print("error rollback")
        print(chk)
        db.rollback()
    else:
        db.commit()
    finally:
        db.close()
