import json
import requests
import gzip
import datetime
import time
import db_func
import argparse

url = "http://api.syosetu.com/novelapi/api/"

def get_allcount():
    payload = {"out": "json", "gzip": "5","lim": "1"}

    retry = 0
    while retry < 5:
        try:
            res = requests.get(url, params=payload)
            res.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"connection error: not get allcount ({e})")
            retry = retry + 1
            time.sleep(10)
    else:
        print("allcountの取得に失敗しました。処理を終了します。")
        exit(1)

    cont = gzip.decompress(res.content).decode("utf-8")
    res_json = json.loads(cont)
    allcount = int(res_json[0]["allcount"])

    return allcount

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


# ========================================================================================================================== #
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="なろうAPIデータ取得",
        description="なろうAPIから全小説データを取得し、JSONファイルに出力します。"
    )
    parser.add_argument(
        '-o', '--outfile',
        type=str,
        default="temp.json",
        help="出力するJSONファイル名 (デフォルト: temp.json)"
    )
    args = parser.parse_args()

    lastup = int(datetime.datetime.now().timestamp())
    print("なろうAPIから作品総数を取得しています...")
    allcount = get_allcount()
    print(f"作品総数: {allcount}")

    cnt = check_count()
    if cnt < 0:
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
                res.raise_for_status()
                break
            except Exception as e:
                print(f"connection error ({e})")
                retry = retry + 1
                time.sleep(10)
        else:
            print("APIからのデータ取得に失敗しました。処理を中断します。")
            exit(1)

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

    print(f"取得したデータを {args.outfile} に出力します...")
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=4)

    print("出力が完了しました。")
    exit()
