from typing import Any, Dict, List, Optional

import database as db
import schemas
import services.todo_service as todo_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from mysql.connector.connection import MySQLConnection

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
        add_todo = todo_service.add_todo_service(todo, current_user.id, cnx)
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
        todos = todo_service.get_todos(done, category, search, current_user, cnx)
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
        return todo_service.get_todo(todo_id, current_user, cnx)
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
        return schemas.TodoUpdateResponse(
            success=True,
            message="수정 성공",
            data=todo_service.modify_todo(todo_id, todo, current_user, cnx),
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
        todo_service.delete_todo(todo_id, current_user.id, cnx)
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
