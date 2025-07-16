import datetime

import schemas
from config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    config,
)
from fastapi import FastAPI, HTTPException
from jose import jwt
from mysql_connection import (
    ensure_tables_exist,
    get_connection,
    insert_user,
    select_user_by_email_and_password,
)
from passlib.context import CryptContext

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=15
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


@app.on_event("startup")
async def startup_event():
    cnx = get_connection(config)
    if cnx and cnx.is_connected():
        ensure_tables_exist(cnx)
    else:
        print("DB 연결에 실패했습니다.")
        exit(1)


@app.post(
    "/login",
    response_model=schemas.UserLoginResponse,
    responses={
        500: {
            "model": schemas.ErrorResponse,
            "description": "DB 연결에 실패했습니다.",
            "content": {
                "application/json": {
                    "example": {"success": False, "message": "DB 연결에 실패했습니다."}
                }
            },
        },
        404: {
            "model": schemas.ErrorResponse,
            "description": "존재하지 않는 이메일입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "존재하지 않는 이메일입니다.",
                    }
                }
            },
        },
        401: {
            "model": schemas.ErrorResponse,
            "description": "비밀번호가 일치하지 않습니다.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "비밀번호가 일치하지 않습니다.",
                    }
                }
            },
        },
    },
)
def login(request: schemas.UserLoginRequest, response: schemas.UserLoginResponse):
    email = request.email
    password = request.password
    # 필수 입력값 누락
    if not email or not password:
        return schemas.ErrorResponse(
            success=False,
            message="이메일 또는 비밀번호가 비어있습니다",
        )
    cnx = get_connection(config)
    if not cnx or not cnx.is_connected():
        raise HTTPException(status_code=500, detail="DB 연결에 실패했습니다.")
    # 사용자 조회
    user = select_user_by_email_and_password(email, password, cnx)
    if not user:
        raise HTTPException(
            status_code=404, detail="이메일 또는 비밀번호가 일치하지 않습니다."
        )
    user_id, user_name, user_email, _ = user
    # 엑세스 토큰 발급
    access_token_expires = datetime.timedelta(
        minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=access_token_expires,
    )
    # 성공
    return schemas.UserLoginResponse(
        success=True,
        message="로그인 성공",
        data=schemas.UserLoginData(
            token=token,
            user=schemas.PublicUserInfo(id=user_id, email=user_email, name=user_name),
        ),
    )


@app.post(
    "/register",
    response_model=schemas.UserSigninResponse,
    responses={
        500: {
            "model": schemas.ErrorResponse,
            "description": "DB 연결에 실패했습니다.",
            "content": {
                "application/json": {
                    "example": {"success": False, "message": "DB 연결에 실패했습니다."}
                }
            },
        },
        500: {
            "model": schemas.ErrorResponse,
            "description": "DB 연결에 실패했습니다.",
            "content": {
                "application/json": {
                    "example": {"success": False, "message": "DB 연결에 실패했습니다."}
                }
            },
        },
    },
)
# 이메일 형식 체크는 pydantic 모델에서 수행함
def register(request: schemas.UserSigninRequest):
    email = request.email
    password = request.password
    name = request.name
    # 필수 필드 유효성 검사 (email, password, name)
    if not email or not password or not name:
        return {"success": "공백이 존재합니다."}

    cnx = get_connection(config)
    if not cnx or not cnx.is_connected():
        raise HTTPException(status_code=500, detail="DB 연결에 실패했습니다.")
    #  이메일 중복 확인 (DB에서 기존 이메일 있는지 조회) 및 DB에 사용자 정보 저장 (email, 암호화된 password, name)
    if insert_user(email, password, name, cnx):
        return schemas.UserSigninResponse(
            success=True,
            message="회원가입에 성공하셨습니다.",
            data=schemas.PublicUserInfo(id=1, email=email, name=name),
        )
    else:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    # TODO 예외 처리 (DB 연결 실패, 쿼리 오류 등)


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
