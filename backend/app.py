from config import config
from flask import Flask
from mysql_connection import (
    ensure_tables_exist,
    get_all_users,
    get_connection,
    insert_user,
    select_user_by_email,
)

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello World!"


if __name__ == "__main__":
    # cnx = 데이터베이스에 연결된 객체를 의미하는 네이밍
    cnx = get_connection(config)
    if cnx:
        print(cnx)
        ensure_tables_exist(cnx)
        get_all_users(cnx)
        insert_user("chec@naver.com", "qweqweqwe", "asda", cnx)
        select_user_by_email("chec@naver.com", cnx)
        cnx.close()
    else:
        print("DB 연결 실패")
    app.run()
