from config import config
from flask import Flask
from mysql_connection import get_all_users, get_connection

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello World!"


if __name__ == "__main__":
    # cnx = 데이터베이스에 연결된 객체를 의미하는 네이밍
    cnx = get_connection(config)
    if cnx:
        print(cnx)
        get_all_users(cnx)
        cnx.close()
    else:
        print("DB 연결 실패")
    app.run()
