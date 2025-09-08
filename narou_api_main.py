import json
import requests
import gzip
import datetime
import pymysql.cursors
import datetime
import time
import pandas as pd

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
    allcount = get_allcount()

    cnt = check_count()
    if cnt >= 0:
        timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    else:
        print("error cnt value")
        exit()


    all_novels_list = []
    seen_ncodes = set()
    # APIの仕様上、少し多めにループさせます
    for i in range(allcount // 500 + 2):
        payload = {"out": "json", "gzip": "5", "lastup":"1073779200-"+str(lastup), "order": "new", "lim": "500"}

        retry = 0
        while retry < 5:
            try:
                res = requests.get(url, params=payload)
                break
            except:
                print("connection error")
                retry = retry + 1
                time.sleep(10)

        # 取得したデータをjsonとして読み込んだあとallcountを削除
        cont = gzip.decompress(res.content).decode("utf-8")
        res_json = json.loads(cont)
        del res_json[0]

        # 重複をチェックしながらリストにデータを追加
        for novel_data in res_json:
            ncode = novel_data.get("ncode")
            if ncode and ncode not in seen_ncodes:
                all_novels_list.append(novel_data)
                seen_ncodes.add(ncode)

        last_general_lastup = res_json[-1]["general_lastup"]
        lastup = datetime.datetime.strptime(last_general_lastup, "%Y-%m-%d %H:%M:%S").timestamp()
        lastup = int(lastup)
        print(res_json[-1]["general_lastup"])

    # narou_json2db.py が期待する {"0": {...}, "1": {...}} の形式に変換
    output_dict = {str(i): novel for i, novel in enumerate(all_novels_list)}

    with open("temp.json", "w", encoding="utf-8") as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=4)

    exit()
