import pymysql.cursors
import pandas as pd
import matplotlib.pyplot as plt


url = "http://api.syosetu.com/novelapi/api/"

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

    try:
        db = db_connect()
        chk = []
        set_sql_data = []
        with db.cursor() as cursor:
            sql = "SELECT ncode, title, global_point FROM contents_tbl WHERE general_firstup BETWEEN '2021-01-01 00:00:00' AND '2021-12-31 23:59:59' ORDER BY global_point DESC LIMIT 0, 500"
            cursor.execute(sql)
            res = cursor.fetchall()
       

        result = []
        for i in res:
            dict_l = {"len" : len(i["title"])}
            i.update(dict_l)
            result.append(i)
            if dict_l["len"] == 1:
                print(i)
                
        df = pd.DataFrame(result)
        df["len"].hist()
        print( df["len"].describe() )

        plt.show()    

    except:
        print("error")
        print(chk)
    finally:
        db.close()
