import datetime

import schemas
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.security import HTTPBearer
from mysql.connector.connection import MySQLConnection
from mysql_connection import (
    add_todo_into_database,
    delete_todo_from_database,
    delete_user,
    get_current_user,
    get_db_connection,
    get_todo_from_database,
    get_total_todos_from_datbase,
    insert_user,
    put_todo_from_database,
    select_user_by_email_and_password,
    toggle_todo_from_database,
)
from utils import create_access_token
from typing import Optional

app = FastAPI()


security = HTTPBearer()


@app.post(
    "/login",
    response_model=schemas.LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        401: {"model": schemas.ErrorResponse, "description": "비밀번호 불일치"},
        404: {"model": schemas.ErrorResponse, "description": "존재하지 않는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def login(
    request: schemas.LoginRequest, cnx: MySQLConnection = Depends(get_db_connection)
):
    try:
        email = request.email
        password = request.password
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이메일을 입력해주세요."
            )
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호를 입력해주세요",
            )
        user = select_user_by_email_and_password(email, password, cnx)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 유저입니다.",
            )
        user_id, user_name, user_email = user
        return schemas.LoginResponse(
            success=True,
            message="로그인에 성공하셨습니다.",
            data=schemas.LoginData(
                token=create_access_token(
                    data={"sub": str(user_id), "email": user_email}
                ),
                user=schemas.PublicUser(id=user_id, email=user_email, name=user_name),
            ),
        )
    except HTTPException:
        raise
    except Exception as error:
        print("Login Unexpected error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 로그인에 실패하였습니다.",
        )


@app.post(
    "/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        409: {"model": schemas.ErrorResponse, "description": "이미 존재하는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def register(
    request: schemas.RegisterRequest, cnx: MySQLConnection = Depends(get_db_connection)
):
    try:
        email = request.email
        password = request.password
        name = request.name
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이메일을 입력해주세요."
            )
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호를 입력해주세요",
            )
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이름을 입력해주세요"
            )
        user_id = insert_user(email, password, name, cnx)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 이메일입니다.",
            )

        return schemas.RegisterResponse(
            success=True,
            message="회원가입에 성공하셨습니다.",
            data=schemas.PublicUser(id=user_id, email=email, name=name),
        )
    except HTTPException:
        raise
    except Exception as err:
        # 내부 로그만 출력하고 사용자에겐 일반 메시지
        print("Register Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 회원가입에 실패했습니다.",
        )


@app.post(
    "/logout",
    response_model=schemas.LogoutResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def logout():
    try:
        return schemas.LogoutResponse(success=True, message="로그아웃 성공")
    except HTTPException:
        raise
    except Exception as error:
        print("서버 오류로 로그아웃에 실패하였습니다.", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 회원탈퇴에 실패하였싑니다.",
        )


@app.post(
    "/withdraw",
    response_model=schemas.WithdrawResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def withdraw(
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx: MySQLConnection = Depends(get_db_connection),
):
    try:
        delete_user(current_user.id, cnx)
        return schemas.WithdrawResponse(success=True, message="회원탈퇴 성공")
    except HTTPException:
        raise
    except Exception as error:
        print("withdraw Unexpected error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 회원탈퇴에 실패하였습니다.",
        )


@app.get(
    "/user",
    response_model=schemas.MeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": schemas.ErrorResponse, "description": "인증 필요"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def info_me(current_user: schemas.PublicUser = Depends(get_current_user)):
    try:
        return schemas.MeResponse(
            success=True, message="유저 본인정보 조회 성공", data=current_user
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류로 유저 정보 조회에 실패하였습니다. {err}",
        )


@app.post(
    "/todos",
    response_model=schemas.TodoCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def add_todo(
    todo: schemas.TodoCreateRequest,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx: MySQLConnection = Depends(get_db_connection),
):
    try:
        if (
            not todo.title
            or not todo.description
            or not todo.category
            or not todo.duedate
            or not todo.priority
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="할일 내용을 입력해주세요.",
            )
        todo_id = add_todo_into_database(todo, current_user.id, cnx)
        if not todo_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DB 에러입니다.",
            )
        return schemas.TodoCreateResponse(
            success=True,
            message="할일 등록 성공",
            data=schemas.Todo(
                id=todo_id,
                title=todo.title,
                description=todo.description,
                category=todo.category,
                priority=todo.priority,
                duedate=datetime.date.today(),
                done=False,
                created_at=datetime.datetime.now(),
            ),
        )
    except HTTPException:
        raise
    except Exception as err:
        print(f"add new post error {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 할일 추가에 실패하였습니다.",
        )


@app.get(
    "/todos",
    response_model=schemas.TodoListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todos(
    done: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx: MySQLConnection = Depends(get_db_connection),
):
    try:
        todos_raw = get_total_todos_from_datbase(
            current_user.id, cnx, done=done, category=category
        ) or []
        todos = []
        for todo in todos_raw:
            todo["done"] = bool(todo["done"])
            todos.append(schemas.Todo(**todo))
        return schemas.TodoListResponse(
            success=True,
            message="할일 목록조회 성공",
            data=schemas.TodoListData(
                todos=todos,
                pagination=schemas.PaginationMeta(
                    currentPage=1, totalPages=1, totalItems=len(todos)
                ),
            ),
        )
    except Exception as err:
        print("get_todos Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할일 목록 조회 오류: {err}",
        )


@app.get(
    "/todos/{todo_id}",
    response_model=schemas.TodoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx: MySQLConnection = Depends(get_db_connection),
):
    try:
        todo = get_todo_from_database(current_user.id, todo_id, cnx)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="조회한 할일이 업습니다."
            )
        todo["done"] = bool(todo["done"])
        return schemas.TodoResponse(
            success=True,
            message=f"{todo_id}번째 할일 조회 성공",
            data=schemas.Todo(**todo),
        )
    except HTTPException:
        raise
    except Exception as err:
        print("get_todo Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할일 조회 오류: {err}",
        )


@app.put(
    "/todos/{todo_id}",
    response_model=schemas.TodoUpdateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def modify_todo(
    todo_id: int,
    todo: schemas.TodoUpdateRequest,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx: MySQLConnection = Depends(get_db_connection),
):
    try:
        # 1. 존재하지 않는 할일 ID 확인
        existing_todo = get_todo_from_database(current_user.id, todo_id, cnx)
        if not existing_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="할일이 존재하지 않습니다.",
            )
        # 2. 필드별 공백/유효성 체크 (입력된 값만 검사)
        if todo.title is not None and not todo.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="제목이 공백입니다.",
            )
        if todo.description is not None and not todo.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="설명이 공백입니다.",
            )
        if todo.category is not None and not str(todo.category).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카테고리가 공백입니다.",
            )
        if todo.priority is not None and not str(todo.priority).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="우선순위가 공백입니다.",
            )
        if todo.duedate is not None and str(todo.duedate).strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="마감일이 공백입니다.",
            )
        if todo.done is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="done 값은 boolean이어야 합니다.",
            )
        # 3. DB 수정
        modified_todo = put_todo_from_database(current_user.id, todo_id, todo, cnx)
        if not modified_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="할일이 존재하지 않습니다.",
            )
        modified_todo["done"] = bool(modified_todo["done"])
        return schemas.TodoUpdateResponse(
            success=True, message="수정 성공", data=schemas.Todo(**modified_todo)
        )
    except HTTPException:
        raise
    except Exception as err:
        print("modify_todo Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할일 수정 오류: {err}",
        )


@app.delete(
    "/todos/{todo_id}",
    response_model=schemas.DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def delete_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx: MySQLConnection = Depends(get_db_connection),
):
    try:
        result = delete_todo_from_database(current_user.id, todo_id, cnx)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="할일이 존재하지 않습니다.",
            )
        return schemas.DeleteResponse(
            success=True, message=f"{todo_id}번째 할일 삭제 성공"
        )
    except HTTPException:
        raise
    except Exception as err:
        print("delete_todo Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할일 삭제 오류: {err}",
        )


@app.patch(
    "/todos/{todo_id}/toggle",
    response_model=schemas.ToggleResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def toggle_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx: MySQLConnection = Depends(get_db_connection),
):
    try:
        updated_todo = toggle_todo_from_database(current_user.id, todo_id, cnx)
        if not updated_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="할일이 존재하지 않습니다.",
            )
        updated_todo["done"] = bool(updated_todo["done"])
        return schemas.ToggleResponse(
            success=True,
            message=f"할일 상태가 {updated_todo['done']}로 변경되었습니다.",
        )
    except Exception as err:
        print("toggle_todo Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토글 오류: {err}",
        )
