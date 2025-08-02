from typing import Any, Generator, Optional, cast

import models
import mysql.connector
import schemas
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mysql.connector import MySQLConnection, errorcode
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from utils import decode_jwt_token, extract_user_info_from_payload, get_password_hash

security = HTTPBearer()

engine = create_engine(
    "mysql+mysqlconnector://root:1234@127.0.0.1:3306/todo_app", pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cnx: Session = Depends(get_db),
):
    try:
        token = credentials.credentials
        payload = decode_jwt_token(token)
        user_info = extract_user_info_from_payload(payload)
        user_email = user_info["email"]
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    user = select_user_by_email(user_email, cnx)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 유저입니다.",
        )
    return schemas.PublicUser(id=user.id, email=user.email, name=user.name)


def get_connection(config: Any):
    try:
        cnx = mysql.connector.connect(**config)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None


def email_exist(email: str, session: Any) -> bool:
    stmt = select(models.User).where(models.User.email == email)
    user = session.scalars(stmt)
    if user:
        return False
    return True


def create_user(
    email: str, password: str, name: str, session: Session
) -> Optional[int]:
    hashed_password = get_password_hash(password)
    new_user = models.User(usr_nm=name, pwd=hashed_password, email=email)
    try:
        session.add(new_user)
        session.commit()
        return new_user.usr_id
    except Exception as e:
        session.rollback()
        print("DB 유저 삽입 에러", e)
        return None


def delete_user(user_id: int, session: Session):
    try:
        stmt = select(models.User).where(models.User.usr_id == user_id)
        target_user = session.scalars(stmt).one_or_none()
        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="탈퇴할 사용자를 찾을 수 없습니다.",
            )
        session.delete(target_user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("DB 유저 삭제 에러", e)
        return None


def select_user_by_email(email: str, session: Any):
    stmt = select(models.User).where(models.User.email == email)
    user = session.scalars(stmt).one()
    return schemas.UserInDB(
        id=user.usr_id, name=user.usr_nm, email=user.email, password=user.pwd
    )


def add_todo_into_database(
    todo: schemas.TodoCreateRequest,
    user_id: int,
    session: Session,
):
    new_todo = models.Todo(
        todo_title=todo.title,
        todo_dtl=todo.description,
        ctgy=todo.category,
        priority_lvl=todo.priority,
        due_dt=todo.duedate,
        usr_id=user_id,
    )
    try:
        session.add(new_todo)
        session.commit()
        return new_todo.todo_id
    except Exception as e:
        session.rollback()
        print("할일 추가 에러:", e)
        raise HTTPException(
            status_code=500,
            detail="할일을 추가하는 중 데이터베이스 오류가 발생했습니다.",
        )


def get_total_todos_from_datbase(
    user_id: int,
    session: Session,
    done: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    stmt = select(models.Todo).where(models.Todo.usr_id == user_id)

    if done is not None:
        stmt = stmt.where(models.Todo.yn_done == done)

    if category is not None:
        stmt = stmt.where(models.Todo.ctgy == category)

    if search is not None and search.strip() != "":
        stmt = stmt.where(models.Todo.todo_title.like(f"%{search}%"))

    result = session.execute(stmt)
    todos = result.scalars().all()
    return todos


def get_todo_from_database(
    user_id: int, todo_id: int, cnx: MySQLConnection
) -> schemas.Todo | None:
    with cnx.cursor(dictionary=True) as cursor:
        sql = "SELECT * FROM todo WHERE usr_id = %s AND todo_id = %s"
        cursor.execute(sql, (user_id, todo_id))
        raw_row = cursor.fetchone()
        if raw_row is None:
            return None
        row = cast(dict[str, Any], raw_row)
        return schemas.Todo(
            id=row["todo_id"],
            title=row["todo_title"],
            description=row["todo_dtl"],
            done=bool(row["yn_done"]),
            category=row["ctgy"],
            priority=row["priority_lvl"],
            duedate=row["due_dt"],
            created_at=row["created_dt"],
        )


def put_todo_from_database(
    user_id: int, todo_id: int, todo: schemas.TodoUpdateRequest, cnx: MySQLConnection
) -> schemas.Todo | None:
    update_todo = todo.model_dump(exclude_unset=True)

    key_mapping = {
        "title": "todo_title",
        "description": "todo_dtl",
        "category": "ctgy",
        "duedate": "due_dt",
        "priority": "priority_lvl",
        "done": "yn_done",
    }

    update_todo_db = {}
    for key, value in update_todo.items():
        db_key = key_mapping.get(key)
        if db_key:
            update_todo_db[db_key] = value
        else:
            # 매핑 없는 키는 필요에 따라 넣거나 무시
            update_todo_db[key] = value

    if not update_todo_db:
        return None

    with cnx.cursor(dictionary=True) as cursor:
        set_clause = ", ".join(f"{col} = %s" for col in update_todo_db.keys())
        sql = f"UPDATE todo SET {set_clause} WHERE usr_id = %s AND todo_id = %s"
        values = list(update_todo_db.values()) + [user_id, todo_id]
        cursor.execute(sql, values)
        cnx.commit()

        cursor.execute(
            "SELECT * FROM todo WHERE usr_id = %s AND todo_id = %s",
            (user_id, todo_id),
        )
        raw_row = cursor.fetchone()
        if raw_row is None:
            return None
        row = cast(dict[str, Any], raw_row)
        return schemas.Todo(
            id=row["todo_id"],
            title=row["todo_title"],
            description=row["todo_dtl"],
            done=bool(row["yn_done"]),
            category=row["ctgy"],
            priority=row["priority_lvl"],
            duedate=row["due_dt"],
            created_at=row["created_dt"],
        )


def delete_todo_from_database(user_id: int, todo_id: int, cnx: Any):
    try:
        with cnx.cursor() as cursor:
            sql = "DELETE FROM todo WHERE usr_id = %s AND todo_id = %s"
            cursor.execute(sql, (user_id, todo_id))
            cnx.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print("DB 할일 삭제 에러:", e)
        return False


def toggle_todo_from_database(user_id: int, todo_id: int, cnx: Any):
    with cnx.cursor(dictionary=True) as cursor:
        sql = "SELECT * FROM todo WHERE usr_id = %s AND todo_id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="해당 할일을 찾을 수 없습니다.")
        current_done = row["yn_done"]
        new_done = 0 if current_done else 1
        sql = "UPDATE todo SET yn_done = %s WHERE usr_id = %s AND todo_id = %s"
        cursor.execute(sql, (new_done, user_id, todo_id))
        cnx.commit()
        sql = "SELECT * FROM todo WHERE usr_id = %s AND todo_id = %s"
        cursor.execute(sql, (user_id, todo_id))
        updated_row = cursor.fetchone()
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
        return updated_row
