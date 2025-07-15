from config import config
from flask import Flask
from mysql_connection import get_connection

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello World!"


if __name__ == "__main__":
    mydb = get_connection(config)
    print(mydb)
    app.run()
