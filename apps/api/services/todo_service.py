import datetime

import database as db
import schemas
from fastapi import HTTPException, status
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
