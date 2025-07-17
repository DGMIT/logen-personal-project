import datetime

import jwt
import schemas
from config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    config,
)
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mysql_connection import (
    add_todo_into_database,
    delete_user,
    ensure_tables_exist,
    get_connection,
    insert_user,
    select_user_by_email,
    select_user_by_email_and_password,
)

app = FastAPI()


security = HTTPBearer()


def get_db_connection():
    cnx = get_connection(config)
    try:
        yield cnx
    finally:
        if cnx and cnx.is_connected():
            cnx.close()


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    if not JWT_SECRET_KEY or not JWT_ACCESS_TOKEN_EXPIRE_MINUTES or not JWT_ALGORITHM:
        raise HTTPException(status_code=500, detail="JWT 설정이 올바르지 않습니다.")

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str):
    if not JWT_SECRET_KEY or not JWT_ACCESS_TOKEN_EXPIRE_MINUTES or not JWT_ALGORITHM:
        raise HTTPException(status_code=500, detail="JWT 설정이 올바르지 않습니다.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")


def extract_user_info_from_payload(payload: dict):
    user_id = payload.get("sub")
    user_email = payload.get("email")
    if not user_id or not user_email:
        raise HTTPException(status_code=401, detail="토큰에 필요한 정보가 없습니다.")
    return user_id, user_email


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cnx=Depends(get_db_connection),
):
    token = credentials.credentials
    print("token", token)
    payload = decode_jwt_token(token)
    user_id, user_email = extract_user_info_from_payload(payload)
    user = select_user_by_email(user_email, cnx)
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    return schemas.PublicUser(id=user[0], email=user[2], name=user[1])


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
    response_model=schemas.LoginResponse,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        401: {"model": schemas.ErrorResponse, "description": "비밀번호 불일치"},
        404: {"model": schemas.ErrorResponse, "description": "존재하지 않는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def login(request: schemas.LoginRequest):
    try:
        email = request.email
        password = request.password
        if not email or not password:
            raise HTTPException(
                status_code=400, detail="이메일 또는 비밀번호가 비어있습니다"
            )
        cnx = get_connection(config)
        if not cnx or not cnx.is_connected():
            raise HTTPException(status_code=500, detail="DB 연결에 실패했습니다.")
        user = select_user_by_email_and_password(email, password, cnx)
        if not user:
            raise HTTPException(status_code=404, detail="존재하지 않는 이메일입니다.")
        user_id, user_name, user_email, _ = user
        return schemas.LoginResponse(
            success=True,
            message="로그인 성공",
            data=schemas.LoginData(
                token=create_access_token(
                    data={"sub": str(user_id), "email": user_email}
                ),
                user=schemas.PublicUser(id=user_id, email=user_email, name=user_name),
            ),
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"로그인 오류: {err}")


@app.post(
    "/register",
    response_model=schemas.RegisterResponse,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        409: {"model": schemas.ErrorResponse, "description": "이미 존재하는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def register(request: schemas.RegisterRequest):
    try:
        email = request.email
        password = request.password
        name = request.name
        if not email or not password or not name:
            raise HTTPException(status_code=400, detail="공백이 존재합니다.")
        cnx = get_connection(config)
        if not cnx or not cnx.is_connected():
            raise HTTPException(status_code=500, detail="DB 연결에 실패했습니다.")
        if insert_user(email, password, name, cnx):
            return schemas.RegisterResponse(
                success=True,
                message="회원가입에 성공하셨습니다.",
                data=schemas.PublicUser(id=1, email=email, name=name),
            )
        else:
            raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"회원가입 오류: {err}")


@app.post(
    "/logout",
    response_model=schemas.LogoutResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def logout(current_user: schemas.PublicUser = Depends(get_current_user)):
    return schemas.LogoutResponse(success=True, message="로그아웃 성공")


@app.post(
    "/withdraw",
    response_model=schemas.WithdrawResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def withdraw(
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
    print("withdraw current_user", current_user)
    delete_user(current_user.id, cnx)
    return schemas.WithdrawResponse(success=True, message="회원탈퇴 성공")


@app.get(
    "/user",
    response_model=schemas.MeResponse,
    responses={
        401: {"model": schemas.ErrorResponse, "description": "인증 필요"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def info_me(current_user: schemas.PublicUser = Depends(get_current_user)):
    return schemas.MeResponse(
        success=True, message="유저 본인정보 조회 성공", data=current_user
    )


@app.post(
    "/todos",
    response_model=schemas.TodoCreateResponse,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def add_todo(
    todo: schemas.TodoCreateRequest,
    curret_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
    add_todo_into_database(todo, curret_user.id, cnx)
    return schemas.TodoCreateResponse(
        success=True,
        message="할일 등록 성공",
        data=schemas.Todo(
            id=1,
            title="샘플 할일",
            description="샘플 설명",
            category="개인",
            priority="보통",
            dueDate=datetime.date.today(),
            completed=False,
            createdAt=datetime.datetime.now(),
            updatedAt=datetime.datetime.now(),
        ),
    )


@app.get(
    "/todos/{id}",
    response_model=schemas.TodoResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todo(id: int, current_user: schemas.PublicUser = Depends(get_current_user)):
    return schemas.TodoResponse(
        success=True,
        message=f"{id}번째 할일 조회 성공",
        data=schemas.Todo(
            id=id,
            title=f"{id}번째 할일",
            description="샘플 설명",
            category="개인",
            priority="보통",
            dueDate=datetime.date.today(),
            completed=False,
            createdAt=datetime.datetime.now(),
            updatedAt=datetime.datetime.now(),
        ),
    )


@app.get(
    "/todos",
    response_model=schemas.TodoListResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todos(current_user: schemas.PublicUser = Depends(get_current_user)):
    return schemas.TodoListResponse(
        success=True,
        message="할일 목록조회 성공",
        data=schemas.TodoListData(
            todos=[
                schemas.Todo(
                    id=1,
                    title="첫 번째 할일",
                    description="샘플 설명",
                    category="개인",
                    priority="보통",
                    dueDate=datetime.date.today(),
                    completed=False,
                    createdAt=datetime.datetime.now(),
                    updatedAt=datetime.datetime.now(),
                ),
                schemas.Todo(
                    id=2,
                    title="두 번째 할일",
                    description="샘플 설명",
                    category="업무",
                    priority="높음",
                    dueDate=datetime.date.today(),
                    completed=True,
                    createdAt=datetime.datetime.now(),
                    updatedAt=datetime.datetime.now(),
                ),
            ],
            pagination=schemas.PaginationMeta(
                currentPage=1, totalPages=1, totalItems=2
            ),
        ),
    )


@app.put(
    "/todos/{id}",
    response_model=schemas.TodoUpdateResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def modify_todo(id: int, current_user: schemas.PublicUser = Depends(get_current_user)):
    return schemas.TodoUpdateResponse(
        success=True,
        message=f"{id}번째 할일 수정 성공",
        data=schemas.Todo(
            id=id,
            title=f"수정된 {id}번째 할일",
            description="수정된 설명",
            category="학습",
            priority="높음",
            dueDate=datetime.date.today(),
            completed=False,
            createdAt=datetime.datetime.now(),
            updatedAt=datetime.datetime.now(),
        ),
    )


@app.delete(
    "/todos/{id}",
    response_model=schemas.DeleteResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def delete_todo(id: int, current_user: schemas.PublicUser = Depends(get_current_user)):
    return schemas.DeleteResponse(success=True, message=f"{id}번째 할일 삭제 성공")


@app.patch(
    "/todos/{id}/toggle",
    response_model=schemas.ToggleResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def toggle_todo(id: int, current_user: schemas.PublicUser = Depends(get_current_user)):
    return schemas.ToggleResponse(
        success=True, message=f"{id}번째 할일 완료 상태 변경 성공"
    )
