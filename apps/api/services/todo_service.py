import datetime
from typing import Any, Dict, List, Optional

import database as db
import schemas
from fastapi import Depends, HTTPException, Query, status
from mysql.connector import MySQLConnection


def add_todo_service(
    todo: schemas.TodoCreateRequest, user_id: int, cnx: MySQLConnection
) -> schemas.Todo:
    todo_id = db.add_todo_into_database(todo, user_id, cnx)
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


def get_todos(
    done: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    todos_raw: List[Dict[str, Any]] = (
        db.get_total_todos_from_datbase(
            current_user.id, cnx, done=done, category=category, search=search
        )
        or []
    )

    todos: List[schemas.Todo] = []
    for todo in todos_raw:
        todo_dict: Dict[str, Any] = {
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
    return todos
