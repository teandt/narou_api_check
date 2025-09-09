import pymysql.cursors
from dotenv import load_dotenv
import os

load_dotenv(".env")

def db_connect():
    db = pymysql.connect(host=os.environ.get("DB_HOST"),
                        port=int(os.environ.get("DB_PORT")),
                        user=os.environ.get("MYSQL_USER"),
                        password=os.environ.get("MYSQL_PASSWORD"),
                        database=os.environ.get("MYSQL_DATABASE"),
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)
    return db
