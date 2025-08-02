import datetime
from typing import Any, Dict, List, Optional

import database as db
import schemas
from fastapi import Depends, HTTPException, Query, status
from mysql.connector import MySQLConnection
from sqlalchemy.orm import Session


def add_todo_service(
    todo: schemas.TodoCreateRequest, user_id: int, session: Session
) -> schemas.Todo:
    todo_id = db.add_todo_into_database(todo, user_id, session)
    if not todo_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DB 에러입니다.",
        )
    return schemas.Todo(
        id=todo_id,
        title=todo.title,
        description=todo.description,
        category=todo.category,
        priority=todo.priority,
        duedate=datetime.date.today(),
        done=False,
        created_at=datetime.datetime.now(),
    )


def get_todos_service(
    user_id: int,
    done: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: Session = Depends(db.get_db),
):
    todos_raw: List[Dict[str, Any]] = (
        db.get_total_todos_from_datbase(
            user_id, session, done=done, category=category, search=search
        )
        or []
    )

    todos: List[schemas.Todo] = []
    for todo in todos_raw:
        todo_dict: Dict[str, Any] = {
            "id": todo.todo_id,
            "title": todo.todo_title,
            "description": todo.todo_dtl,
            "category": todo.ctgy,
            "priority": todo.priority_lvl,
            "duedate": todo.due_dt,
            "done": bool(todo.yn_done),
            "created_at": todo.created_dt,
            "user_id": todo.usr_id,
        }
        todos.append(schemas.Todo(**todo_dict))
    return todos


def get_todo_service(
    todo_id: int,
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db),
):
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


def modify_todo_service(
    todo_id: int,
    todo: schemas.TodoUpdateRequest,
    user_id: int,
    cnx: MySQLConnection = Depends(db.get_db),
):
    existing_todo = db.get_todo_from_database(user_id, todo_id, cnx)
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
    modified_todo = db.put_todo_from_database(user_id, todo_id, todo, cnx)
    if not modified_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할일이 존재하지 않습니다.",
        )
    return modified_todo


def delete_todo_service(
    todo_id: int,
    user_id: int,
    cnx: MySQLConnection = Depends(db.get_db),
):
    result = db.delete_todo_from_database(user_id, todo_id, cnx)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할일이 존재하지 않습니다.",
        )


def toggle_todo_service(
    todo_id: int,
    user_id: int,
    cnx: MySQLConnection = Depends(db.get_db),
) -> None:
    updated_todo = db.toggle_todo_from_database(user_id, todo_id, cnx)
    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할일이 존재하지 않습니다.",
        )
    updated_todo["yn_done"] = bool(updated_todo["yn_done"])
    return updated_todo
