import ijson
import requests
import gzip
import datetime
import pymysql.cursors
import time

url = "http://api.syosetu.com/novelapi/api/"

def db_connect():
    db = pymysql.connect(host='localhost',
                        port=3306,
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

    cnt = check_count()
    if cnt < 0:
        print("error cnt value")
        exit()

    timestamp = datetime.datetime.now().isoformat(timespec='seconds')

    db = None
    chk = []
    try:
        with open("../tempdata/temp.json", "rb") as f:
            data_iterator = ijson.kvitems(f, '')

            db = db_connect()
            with db.cursor() as cursor:
                sql = "UPDATE parameter_tbl SET parameter_value = %s WHERE parameter_name = 'counter'"
                cursor.execute(sql, (cnt + 1))

                sql = "INSERT INTO count_timestamp_tbl SET count = %s, timestamp = %s"
                cursor.execute(sql, (cnt + 1, timestamp))

                #sql = "INSERT INTO count_allcount_t`bl SET count = %s, allcount = %s"
                #cursor.execute(sql, (cnt + 1, allcount))

                print("start: ", datetime.datetime.now())
                set_sql_data = []
                bulk_cnt = 0

                sql_insert = """INSERT INTO contents_tbl 
                    (count , ncode , title , userid , writer , story , biggenre , genre , 
                    gensaku , keyword , general_firstup , general_lastup , novel_type , end , general_all_no , 
                    length , time , isstop , isr15 , isbl , isgl , iszankoku , istensei , istenni , 
                    global_point , daily_point , weekly_point , monthly_point , 
                    quarter_point , yearly_point , fav_novel_cnt , impression_cnt , review_cnt , all_point , 
                    all_hyoka_cnt , sasie_cnt , kaiwaritu , novelupdated_at , updated_at) 
                    VALUES (    %s, %s, %s, %s, %s, %s, %s, %s, 
                                %s, %s, %s, %s, %s, %s, %s, 
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                %s, %s, %s, %s, 
                                %s, %s, %s, %s, %s, %s, 
                                %s, %s, %s, %s, %s )"""

                for index, i in data_iterator:
                    chk = i
                    if("ncode" not in i):
                        raise Exception(f"ncode not found in record: {i}")

                    set_sql_data_tmp = (cnt + 1, i["ncode"], i["title"], i["userid"], i["writer"], i["story"], i["biggenre"], i["genre"],
                                        i["gensaku"], i["keyword"], i["general_firstup"], i["general_lastup"], i["novel_type"], i["end"], i["general_all_no"], 
                                        i["length"], i["time"], i["isstop"], i["isr15"], i["isbl"], i["isgl"], i["iszankoku"], i["istensei"], i["istenni"], 
                                        i["global_point"], i["daily_point"], i["weekly_point"], i["monthly_point"], 
                                        i["quarter_point"], i["yearly_point"], i["fav_novel_cnt"], i["impression_cnt"], i["review_cnt"], i["all_point"], 
                                        i["all_hyoka_cnt"], i["sasie_cnt"], i["kaiwaritu"], i["novelupdated_at"], i["updated_at"])
                    set_sql_data.append(set_sql_data_tmp)
                    bulk_cnt += 1

                    if(bulk_cnt >= 1000):
                        cursor.executemany(sql_insert, set_sql_data)
                        set_sql_data.clear()
                        bulk_cnt = 0
                
                if(set_sql_data):
                    cursor.executemany(sql_insert, set_sql_data)

                print("end: ", datetime.datetime.now())

    except FileNotFoundError:
        print("error not open file")
        exit()
    except Exception as e:
        print("error rollback")
        print(chk)
        print(e)
        if db:
            db.rollback()
    else:
        if db:
            db.commit()
    finally:
        if db:
            db.close()
