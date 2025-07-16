from config import config
from flask import Flask, request, jsonify
from mysql_connection import ensure_tables_exist, get_connection

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    return jsonify({"message": "로그인 성공"})

@app.route("/register", methods=["POST"])
def register():
    return jsonify({"message": "회원가입 성공"})

@app.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "로그아웃 성공"})

@app.route("/withdraw", methods=["POST"])
def withdraw():
    return jsonify({"message": "회원탈퇴 성공"})

@app.route("/user", methods=["GET"])
def info_me():
    return jsonify({"message": "유저 본인정보 조회 성공"})

@app.route("/todos", methods=["POST"])
def add_todo():
    return jsonify({"message": "할일 등록 성공"})

@app.route("/todos/<int:id>", methods=["GET"])
def get_todo(id):
    return jsonify({"message": f"{id}번째 할일 조회 성공"})

@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify({"message": "할일 목록조회 성공"})

@app.route("/todos/<int:id>", methods=["PUT"])
def modify_todo(id):
    return jsonify({"message": f"{id}번째 할일 수정 성공"})


@app.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    return jsonify({"message": f"{id}번째 할일 삭제 성공"})

@app.route("/todos/<int:id>/toggle", methods=["PATCH"])
def toggle_todo(id):
    return jsonify({"message": f"{id}번째 할일 완료 상태 변경 성공"})


if __name__ == "__main__":
    # cnx = 데이터베이스에 연결된 객체를 의미하는 네이밍
    cnx = get_connection(config)
    if cnx:
        print(cnx)
        ensure_tables_exist(cnx)
    else:
        print("DB 연결 실패")
    app.run()
