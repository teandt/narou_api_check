import argparse
import datetime
import sys

import ijson

import db_func


CONTENTS_COLUMNS = (
    "count",
    "ncode",
    "title",
    "userid",
    "writer",
    "story",
    "biggenre",
    "genre",
    "gensaku",
    "keyword",
    "general_firstup",
    "general_lastup",
    "novel_type",
    "end",
    "general_all_no",
    "length",
    "time",
    "isstop",
    "isr15",
    "isbl",
    "isgl",
    "iszankoku",
    "istensei",
    "istenni",
    "global_point",
    "daily_point",
    "weekly_point",
    "monthly_point",
    "quarter_point",
    "yearly_point",
    "fav_novel_cnt",
    "impression_cnt",
    "review_cnt",
    "all_point",
    "all_hyoka_cnt",
    "sasie_cnt",
    "kaiwaritu",
    "novelupdated_at",
    "updated_at",
)

CONTENTS_INSERT_SQL = (
    f"INSERT INTO contents_tbl ({', '.join(CONTENTS_COLUMNS)}) "
    f"VALUES ({', '.join(['%s'] * len(CONTENTS_COLUMNS))})"
)


def check_count():
    db = db_func.db_connect()

    try:
        with db.cursor() as cursor:
            sql = "SELECT parameter_value  FROM parameter_tbl WHERE parameter_name='counter'"
            cursor.execute(sql)
            data = cursor.fetchone()
            if data is None:
                print("counter value data is none")
                return -1
            result = data
    finally:
        db.close()

    return result["parameter_value"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="なろう小説データDB登録",
        description="JSONファイルから小説データを読み込み、データベースに登録します。",
    )
    parser.add_argument(
        "-i",
        "--infile",
        type=str,
        default="temp.json",
        help="入力するJSONファイル名 (デフォルト: temp.json)",
    )
    return parser


def build_content_row(count, novel):
    if "ncode" not in novel:
        raise Exception(f"ncode not found in record: {novel}")

    return tuple(
        count if column == "count" else novel[column]
        for column in CONTENTS_COLUMNS
    )


def update_count_metadata(cursor, count, timestamp):
    sql = "UPDATE parameter_tbl SET parameter_value = %s WHERE parameter_name = 'counter'"
    cursor.execute(sql, (count,))

    sql = "INSERT INTO count_timestamp_tbl SET count = %s, timestamp = %s"
    cursor.execute(sql, (count, timestamp))


def insert_contents(cursor, data_iterator, count, batch_size=1000):
    set_sql_data = []

    for index, novel in data_iterator:
        set_sql_data.append(build_content_row(count, novel))

        if len(set_sql_data) >= batch_size:
            cursor.executemany(CONTENTS_INSERT_SQL, list(set_sql_data))
            set_sql_data.clear()

    if set_sql_data:
        cursor.executemany(CONTENTS_INSERT_SQL, list(set_sql_data))


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    cnt = check_count()
    if cnt < 0:
        print("error cnt value")
        sys.exit()

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    db = None
    try:
        print(f"{args.infile} からデータを読み込んでいます...")
        with open(args.infile, "rb") as f:
            data_iterator = ijson.kvitems(f, "")

            db = db_func.db_connect()
            with db.cursor() as cursor:
                new_count = cnt + 1
                update_count_metadata(cursor, new_count, timestamp)

                print("start: ", datetime.datetime.now())
                insert_contents(cursor, data_iterator, new_count)
                print("end: ", datetime.datetime.now())

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {args.infile}")
        sys.exit()
    except Exception as e:
        print("error rollback")
        print(e)
        if db:
            db.rollback()
    else:
        if db:
            db.commit()
    finally:
        if db:
            db.close()

    return 0


if __name__ == "__main__":
    main()
