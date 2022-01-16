import json
import requests
import gzip
import pymysql.cursors


url = "http://api.syosetu.com/novelapi/api/"

payload = {"out": "json", "gzip": "5", "order": "old", "lim": "10"}

res = requests.get(url, params=payload)
cont = gzip.decompress(res.content).decode("utf-8")

res_json = json.loads(cont)

db_connect = pymysql.connect(host='127.0.0.1',
                            port=23306,
                            user='narouDB',
                            password='narouDB',
                            database='narou_db',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)

try:
    with db_connect.cursor() as cursor:
        for i in res_json:
            if("ncode" in i):
                sql = "INSERT INTO contents_tbl SET count = 1, ncode = %s, title = %s"
                cursor.execute(sql, (i["ncode"], i["title"]))
except:
    db_connect.rollback()
    db_connect.close()
finally:
    db_connect.commit()
    db_connect.close()
