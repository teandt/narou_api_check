import pandas as pd
import matplotlib.pyplot as plt
import db_func

url = "http://api.syosetu.com/novelapi/api/"
img_dir = "./img"

def check_count():
    db = db_func.db_connect()

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

def get_title_length_hist(check_year: int, limit_size: int):
    try:
        db = db_func.db_connect()
        cursor = None
        chk = [] # この変数は使われていないようです
        with db.cursor() as cursor:            
            sql = "SELECT ncode, title, global_point FROM contents_tbl WHERE general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59' ORDER BY global_point DESC LIMIT 0, %s"
            cursor.execute(sql, (check_year, check_year, limit_size, ))
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
        
        plt.xlim(0, 100)
        plt.title(f"Title Length Histogram for {check_year} (Top {limit_size})")
        plt.xlabel("Title Length")
        plt.ylabel("Frequency")
        plt.savefig(f"hist_{check_year}_{limit_size}.png")
        plt.show()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()


def get_title_length_mean(start_year: int, end_year: int, limit_size: int):
    try:
        db = db_func.db_connect()
        chk = []
        mean_data = []
        df_mean = pd.DataFrame(columns=["len"])
        with db.cursor() as cursor:            
            for i in range(start_year, end_year + 1):
                sql = "SELECT ncode, title, global_point FROM contents_tbl WHERE general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59' ORDER BY global_point DESC LIMIT 0, %s"
                cursor.execute(sql, (i, i, limit_size, ))
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
            plt.title(f"Title Length Mean for {start_year} to {end_year} (TOP:{limit_size})")

            plt.plot(df_mean)
            # start_yearとend_yearの差が小さい場合にstepが0になるのを防ぐ
            if start_year < end_year:
                step = max(1, int((end_year - start_year) / 5))
                plt.xticks(range(start_year, end_year + 1, step))
            else:
                # 年が同じ場合はその年のみ表示
                plt.xticks([start_year])

            plt.ylim(0, 50)
            plt.savefig(f"{img_dir}/plot_top_{start_year}_{end_year}_{limit_size}.png")
            plt.show()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()


def get_nobel_type_nums(start_year: int, end_year: int):
    try:
        db = db_func.db_connect()
        df = pd.DataFrame(columns=["連載", "短編"])
        with db.cursor() as cursor:            
            for i in range(start_year, end_year + 1):
                sql = "select count(*) from contents_tbl where novel_type = 1 and general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59'"
                cursor.execute(sql, (i, i, ))
                r1 = cursor.fetchone()

                sql = "select count(*) from contents_tbl where novel_type = 2 and general_firstup BETWEEN '%s-01-01 00:00:00' AND '%s-12-31 23:59:59'"
                cursor.execute(sql, (i, i, ))
                r2 = cursor.fetchone()

                df.loc[i] = {"連載": r1["count(*)"], "短編": r2["count(*)"]}


        plt.xlim(start_year, end_year)
        plt.title(f"Novel Type Num for {start_year} to {end_year}")
        plt.xlabel("Year")
        plt.ylabel("Count")
        # start_yearとend_yearの差が小さい場合にstepが0になるのを防ぐ
        if start_year < end_year:
            step = max(1, int((end_year - start_year) / 5))
            plt.xticks(range(start_year, end_year + 1, step))
        else:
            # 年が同じ場合はその年のみ表示
            plt.xticks([start_year])

        plt.plot(df)
        # plt.legend() # 凡例の代わりにテキストを直接プロットします

        # 各折れ線の終端にテキストを追加
        # y_pos_r1とy_pos_r2は、テキストが重ならないようにするためのオフセットです
        y_pos_r1 = df.iloc[-1, 0]
        y_pos_r2 = df.iloc[-1, 1]
        plt.text(df.index[-1], y_pos_r1, 'short', va='center')
        plt.text(df.index[-1], y_pos_r2, 'long', va='center')
        plt.savefig(f"{img_dir}/nobel_type_{start_year}-{end_year}.png")
        plt.show()

        print(df)


    except:
        print("error")
        print(cursor._executed)
    finally:
        db.close()

# ========================================================================================================================== #
if __name__ == "__main__":

    #get_title_length_mean(2008, 2024, 10000)
    #get_title_length_hist(2024, 100)
    get_nobel_type_nums(2008, 2024)
