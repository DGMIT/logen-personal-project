from typing import Union

from config import config
from fastapi import FastAPI
from mysql_connection import ensure_tables_exist, get_connection
import schemas

app = FastAPI()

@app.post("/login")
def login(request:schemas.UserLoginRequest):
    email = request.email
    password = request.password

    if not email or not password:
        return schemas.ErrorResponse(
            success=False,
            message="이메일 또는 비밀번호가 비어있습니다",)
    return schemas.UserLoginResponse(
        success=True,
        message="로그인 성공",
        data=schemas.UserLoginData(
            token="1234567890",
            user=schemas.PublicUserInfo(
                id=1,
                email=email,
                name="홍길동"
            )
        )
    )

@app.post("/register")
def register():
    return {"message": "회원가입 성공"}

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
