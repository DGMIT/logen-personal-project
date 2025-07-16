from typing import Union

import schemas
from config import config
from fastapi import FastAPI
from mysql_connection import ensure_tables_exist, get_connection,insert_user,select_user_by_email_and_password

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    cnx = get_connection(config)
    if cnx and cnx.is_connected():
        ensure_tables_exist(cnx)
    else:
        print("DB 연결에 실패했습니다.")
        exit(1)


@app.post("/login")
def login(request: schemas.UserLoginRequest):
    email = request.email
    password = request.password

    if not email or not password:
        return schemas.ErrorResponse(
            success=False,
            message="이메일 또는 비밀번호가 비어있습니다",
        )
    cnx = get_connection(config)
    if cnx and cnx.is_connected():
        ensure_tables_exist(cnx)
        user_id,user_name,user_email,_ = select_user_by_email_and_password(email, password, cnx)
        if user_id and user_email and user_name:
            return schemas.UserLoginResponse(
                success=True,
                message="로그인 성공",
                data=schemas.UserLoginData(
                    token="1234567890",
                    user=schemas.PublicUserInfo(id=user_id, email=user_email, name=user_name),
                ),
            )
        else:
            return schemas.ErrorResponse(
                success=False,
                message="이메일 또는 비밀번호가 일치하지 않습니다.",
            )
    else:
        print("DB 연결에 실패했습니다.")
        exit(1)


@app.post("/register")
def register(request: schemas.UserSigninRequest):
    email = request.email
    password = request.password
    name = request.name

    if not email or not password or not name:
        return {success:"공백이 존재합니다."}

    cnx = get_connection(config)
    if cnx and cnx.is_connected():
        ensure_tables_exist(cnx)
        if insert_user(email, password, name, cnx):
            return schemas.UserSigninResponse(
                success=True,
                message="회원가입에 성공하셨습니다.",
                data=schemas.PublicUserInfo(id=1,email=email,name=name)
            )
        else:
            return schemas.ErrorResponse(
                success=False,
                message="이미 존재하는 이메일입니다.",
            )
    else:
        print("DB 연결에 실패했습니다.")
        exit(1)


@app.post("/logout")
def logout():
    return {"message": "로그아웃 성공"}


@app.post("/withdraw")
def withdraw():
    return {"message": "회원탈퇴 성공"}


@app.get("/user")
def info_me():
    return {"message": "유저 본인정보 조회 성공"}


@app.post("/todos")
def add_todo():
    return {"message": "할일 등록 성공"}


@app.get("/todos/{id}")
def get_todo(id: int):
    return {"message": f"{id}번째 할일 조회 성공"}


@app.get("/todos")
def get_todos():
    return {"message": "할일 목록조회 성공"}


@app.put("/todos/{id}")
def modify_todo(id: int):
    return {"message": f"{id}번째 할일 수정 성공"}


@app.delete("/todos/{id}")
def delete_todo(id: int):
    return {"message": f"{id}번째 할일 삭제 성공"}


@app.patch("/todos/{id}/toggle")
def toggle_todo(id: int):
    return {"message": f"{id}번째 할일 완료 상태 변경 성공"}
