from typing import Optional

import database as db
import schemas
from fastapi import APIRouter, Depends, HTTPException, Query, status
from mysql.connector.connection import MySQLConnection
from services.todo_service import add_todo_service

router = APIRouter(
    prefix="/items",
    dependencies=[Depends(db.get_connection)],
    responses={
        401: {"description": "유효하지 않은 토큰입니다. 다시 로그인해 주세요."},
        500: {"description": "DB 연결 실패"},
    },
)


@router.post(
    "/",
    response_model=schemas.TodoCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
    },
)
def add_todo(
    todo: schemas.TodoCreateRequest,
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        add_todo = add_todo_service(todo, current_user.id, cnx)
        return schemas.TodoCreateResponse(
            success=True, message="할일 등록 성공", data=add_todo
        )
    except HTTPException:
        raise
    except Exception as err:
        print(f"add new post error {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 할일 추가에 실패하였습니다.",
        )


@router.get(
    "/",
    response_model=schemas.TodoListResponse,
    status_code=status.HTTP_200_OK,
)
def get_todos(
    done: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        todos_raw = (
            db.get_total_todos_from_datbase(
                current_user.id, cnx, done=done, category=category, search=search
            )
            or []
        )

        todos = []
        for todo in todos_raw:
            todo_dict = {
                "id": todo["todo_id"],
                "title": todo["todo_title"],
                "description": todo["todo_dtl"],
                "category": todo["ctgy"],
                "priority": todo["priority_lvl"],
                "duedate": todo["due_dt"],
                "done": bool(todo["yn_done"]),
                "created_at": todo["created_dt"],
                "user_id": todo["usr_id"],
            }
            todos.append(schemas.Todo(**todo_dict))
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


@router.get(
    "/{todo_id}",
    response_model=schemas.TodoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
    },
)
def get_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        todo = db.get_todo_from_database(current_user.id, todo_id, cnx)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="조회한 할일이 업습니다."
            )
        return schemas.TodoResponse(
            success=True,
            message=f"{todo_id}번째 할일 조회 성공",
            data=todo,
        )
    except HTTPException:
        raise
    except Exception as err:
        print("get_todo Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할일 조회 오류: {err}",
        )


@router.put(
    "/{todo_id}",
    response_model=schemas.TodoUpdateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
    },
)
def modify_todo(
    todo_id: int,
    todo: schemas.TodoUpdateRequest,
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        # 1. 존재하지 않는 할일 ID 확인
        existing_todo = db.get_todo_from_database(current_user.id, todo_id, cnx)
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
        # done 필드가 있으면 타입만 체크 (boolean이 아니면 에러)
        if todo.done is not None and not isinstance(todo.done, bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="done 값은 boolean이어야 합니다.",
            )
        # 3. DB 수정
        print("before", current_user)
        print("before", todo_id)
        print("befoere", todo)
        modified_todo = db.put_todo_from_database(current_user.id, todo_id, todo, cnx)
        if not modified_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="할일이 존재하지 않습니다.",
            )
        print("modified_todo", modified_todo)
        print("modified_todo", type(modified_todo))
        return schemas.TodoUpdateResponse(
            success=True, message="수정 성공", data=modified_todo
        )
    except HTTPException:
        raise
    except Exception as err:
        print("modify_todo Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할일 수정 오류: {err}",
        )


@router.delete(
    "/{todo_id}",
    response_model=schemas.DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
    },
)
def delete_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        result = db.delete_todo_from_database(current_user.id, todo_id, cnx)
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


@router.patch(
    "/{todo_id}/toggle",
    response_model=schemas.ToggleResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "할일 없음"},
    },
)
def toggle_todo(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        updated_todo = db.toggle_todo_from_database(current_user.id, todo_id, cnx)
        if not updated_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="할일이 존재하지 않습니다.",
            )
        updated_todo["yn_done"] = bool(updated_todo["yn_done"])
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
