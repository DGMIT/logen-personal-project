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
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        401: {"model": schemas.ErrorResponse, "description": "비밀번호 불일치"},
        404: {"model": schemas.ErrorResponse, "description": "존재하지 않는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def login(request: schemas.UserLoginRequest):
    email = request.email
    password = request.password
    if not email or not password:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 비어있습니다")
    cnx = get_connection(config)
    if not cnx or not cnx.is_connected():
        raise HTTPException(status_code=500, detail="DB 연결에 실패했습니다.")
    result = select_user_by_email_and_password(email, password, cnx)
    if not result:
        raise HTTPException(status_code=404, detail="존재하지 않는 이메일입니다.")
    user_id, user_name, user_email, user_password = result
    if user_password != password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    return schemas.UserLoginResponse(
        success=True,
        message="로그인 성공",
        data=schemas.UserLoginData(
            token="1234567890",
            user=schemas.PublicUserInfo(id=user_id, email=user_email, name=user_name),
        ),
    )

@app.post(
    "/register",
    response_model=schemas.UserSigninResponse,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        409: {"model": schemas.ErrorResponse, "description": "이미 존재하는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def register(request: schemas.UserSigninRequest):
    email = request.email
    password = request.password
    name = request.name
    if not email or not password or not name:
        raise HTTPException(status_code=400, detail="공백이 존재합니다.")
    cnx = get_connection(config)
    if not cnx or not cnx.is_connected():
        raise HTTPException(status_code=500, detail="DB 연결에 실패했습니다.")
    if insert_user(email, password, name, cnx):
        return schemas.UserSigninResponse(
            success=True,
            message="회원가입에 성공하셨습니다.",
            data=schemas.PublicUserInfo(id=1, email=email, name=name),
        )
    else:
        raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")

@app.post(
    "/logout",
    response_model=schemas.UserLogoutResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def logout():
    return schemas.UserLogoutResponse(success=True, message="로그아웃 성공")

@app.post(
    "/withdraw",
    response_model=schemas.UserWithdrawResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def withdraw():
    return schemas.UserWithdrawResponse(success=True, message="회원탈퇴 성공")

@app.get(
    "/user",
    response_model=schemas.UserMeResponse,
    responses={
        401: {"model": schemas.ErrorResponse, "description": "인증 필요"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def info_me():
    return schemas.UserMeResponse(success=True, message="유저 본인정보 조회 성공", data=schemas.PublicUserInfo(id=1, email="test@example.com", name="홍길동"))

@app.post(
    "/todos",
    response_model=schemas.TodoCreateResponse,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def add_todo():
    return schemas.TodoCreateResponse(success=True, message="할일 등록 성공", data=None)

@app.get(
    "/todos/{id}",
    response_model=schemas.TodoResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todo(id: int):
    return schemas.TodoResponse(success=True, message=f"{id}번째 할일 조회 성공", data=None)

@app.get(
    "/todos",
    response_model=schemas.TodoListResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todos():
    return schemas.TodoListResponse(success=True, message="할일 목록조회 성공", data=None)

@app.put(
    "/todos/{id}",
    response_model=schemas.TodoUpdateResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def modify_todo(id: int):
    return schemas.TodoUpdateResponse(success=True, message=f"{id}번째 할일 수정 성공", data=None)

@app.delete(
    "/todos/{id}",
    response_model=schemas.DeleteSuccessResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def delete_todo(id: int):
    return schemas.DeleteSuccessResponse(success=True, message=f"{id}번째 할일 삭제 성공")

@app.patch(
    "/todos/{id}/toggle",
    response_model=schemas.ToggleSuccessResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def toggle_todo(id: int):
    return schemas.ToggleSuccessResponse(success=True, message=f"{id}번째 할일 완료 상태 변경 성공")
