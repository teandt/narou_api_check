import pymysql.cursors
import pandas as pd
import matplotlib.pyplot as plt
import re


url = "http://api.syosetu.com/novelapi/api/"

def db_connect():
    db = pymysql.connect(host='narou_api_mariadb',
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

def get_title_length_hist():
    try:
        db = db_connect()
        chk = []
        set_sql_data = []
        start_year = 2022
        end_year = 2022
        with db.cursor() as cursor:            
            sql = "SELECT ncode, title, global_point FROM contents_tbl WHERE general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59' ORDER BY global_point DESC LIMIT 0, 10000"
            cursor.execute(sql, (start_year, end_year,))
            print(cursor._executed)
            res = cursor.fetchall()
       

        result = []
        for i in res:
            dict_l = {"len" : len(i["title"])}
            i.update(dict_l)
            result.append(i)
                
        df = pd.DataFrame(result)
        df["len"].hist()
        print( df["len"].describe() )

        plt.show()    

    except:
        print("error")
        print(cursor._executed)
        print(chk)
    finally:
        db.close()


def get_title_length_mean():
    try:
        db = db_connect()
        chk = []
        mean_data = []
        df_mean = pd.DataFrame(columns=["len"])
        start_year = 2004
        end_year = 2022
        limit_size = 10
        with db.cursor() as cursor:            
            for i in range(start_year, end_year + 1):
                sql = "SELECT ncode, title, global_point FROM contents_tbl WHERE general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59' ORDER BY global_point DESC LIMIT 0, %s"
                cursor.execute(sql, (i, i, limit_size, ))
                #print(cursor._executed)
                res = cursor.fetchall()

                result = []
                for j in res:
                    dict_l = {"len" : len(j["title"])}
                    j.update(dict_l)
                    result.append(j)
                    
                df = pd.DataFrame(result)
                df_mean.loc[i] = df["len"].mean()
            print(df_mean)

            plt.xlim(start_year, end_year)
            
            plt.plot(df_mean)
            plt.show()

    except:
        print("error")
        print(cursor._executed)
        print(chk)
    finally:
        db.close()

def get_nobel_type_nums():
    try:
        db = db_connect()
        df = pd.DataFrame(columns=["long", "short"])
        start_year = 2004
        end_year = 2022
        with db.cursor() as cursor:            
            for i in range(start_year, end_year + 1):
                sql = "select count(*) from contents_tbl where novel_type = 1 and general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59'"
                cursor.execute(sql, (i, i, ))
                r1 = cursor.fetchone()

                sql = "select count(*) from contents_tbl where novel_type = 2 and general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59'"
                cursor.execute(sql, (i, i, ))
                r2 = cursor.fetchone()

                df.loc[i] = [r1["count(*)"], r2["count(*)"]]   


        plt.xlim(start_year, end_year)
        
        plt.plot(df)
        plt.show()

        print(df)


    except:
        print("error")
        print(cursor._executed)
    finally:
        db.close()


# ========================================================================================================================== #
if __name__ == "__main__":

    #get_title_length_mean()
    get_nobel_type_nums()

