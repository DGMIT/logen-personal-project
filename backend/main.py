import datetime

import schemas
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
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

from backend.utils import create_access_token

app = FastAPI()


security = HTTPBearer()


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
def login(request: schemas.LoginRequest, cnx=Depends(get_db_connection)):
    email = request.email
    password = request.password
    if not email:
        raise HTTPException(status_code=400, detail="이메일을 입력해주세요.")
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요")
    user = select_user_by_email_and_password(email, password, cnx)
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 유저입니다.")
    user_id, user_name, user_email, _ = user
    return schemas.LoginResponse(
        success=True,
        message="로그인 성공",
        data=schemas.LoginData(
            token=create_access_token(data={"sub": str(user_id), "email": user_email}),
            user=schemas.PublicUser(id=user_id, email=user_email, name=user_name),
        ),
    )


@app.post(
    "/register",
    response_model=schemas.RegisterResponse,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        409: {"model": schemas.ErrorResponse, "description": "이미 존재하는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def register(request: schemas.RegisterRequest, cnx=Depends(get_db_connection)):
    try:
        email = request.email
        password = request.password
        name = request.name
        if not email:
            raise HTTPException(status_code=400, detail="이메일을 입력해주세요.")
        if not password:
            raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요")
        if not name:
            raise HTTPException(status_code=400, detail="이름을 입력해주세요")
        user_id = insert_user(email, password, name, cnx)
        if not user_id:
            raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")

        return schemas.RegisterResponse(
            success=True,
            message="회원가입에 성공하셨습니다.",
            data=schemas.PublicUser(id=user_id, email=email, name=name),
        )
    except HTTPException:
        raise  # 이미 처리된 예외는 그대로 다시 raise

    except Exception as err:
        # 내부 로그만 출력하고 사용자에겐 일반 메시지
        print("Unexpected error:", err)
        raise HTTPException(
            status_code=500, detail="서버 오류로 회원가입에 실패했습니다."
        )


@app.post(
    "/logout",
    response_model=schemas.LogoutResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def logout(
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
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
    try:
        return schemas.MeResponse(
            success=True, message="유저 본인정보 조회 성공", data=current_user
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"유저 정보 조회 오류: {err}")


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
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
    try:
        todo_id = add_todo_into_database(todo, current_user.id, cnx)
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
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"할일 등록 오류: {err}")


@app.get(
    "/todos/{todo_id}",
    response_model=schemas.TodoResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
    try:
        todo = get_todo_from_database(current_user.id, todo_id, cnx)
        if not todo:
            raise HTTPException(status_code=404, detail="조회한 할일이 업습니다.")
        return schemas.TodoResponse(
            success=True,
            message=f"{todo_id}번째 할일 조회 성공",
            data=schemas.Todo(**todo),
        )
    except HTTPException:
        raise
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"할일 조회 오류: {err}")


@app.get(
    "/todos",
    response_model=schemas.TodoListResponse,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def get_todos(
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
    try:
        return schemas.TodoListResponse(
            success=True,
            message="할일 목록조회 성공",
            data=schemas.TodoListData(
                todos=get_total_todos_from_datbase(current_user.id, cnx),
                pagination=schemas.PaginationMeta(
                    currentPage=1, totalPages=1, totalItems=2
                ),
            ),
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"할일 목록 조회 오류: {err}")


@app.put(
    "/todos/{todo_id}",
    response_model=schemas.TodoUpdateResponse,
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
    cnx=Depends(get_db_connection),
):
    try:
        print("modify_todo_input", todo)
        put_todo_from_database(current_user.id, todo_id, todo, cnx)
        return schemas.TodoUpdateResponse(
            success=True, message="수정 성공", data={"done": True}
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"할일 수정 오류: {err}")


@app.delete(
    "/todos/{todo_id}",
    response_model=schemas.DeleteResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def delete_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
    try:
        delete_todo_from_database(current_user.id, todo_id, cnx)
        return schemas.DeleteResponse(
            success=True, message=f"{todo_id}번째 할일 삭제 성공"
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"할일 삭제 오류: {err}")


@app.patch(
    "/todos/{todo_id}/toggle",
    response_model=schemas.ToggleResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def toggle_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(get_current_user),
    cnx=Depends(get_db_connection),
):
    try:
        updated_todo = toggle_todo_from_database(current_user.id, todo_id, cnx)
        status = "완료" if updated_todo["done"] else "미완료"
        return schemas.ToggleResponse(
            success=True, message=f"할일 상태가 {status}로 변경되었습니다."
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"토글 오류: {err}")
