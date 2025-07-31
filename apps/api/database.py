from typing import Any, Generator, Optional, cast

import mysql.connector
import schemas
from config import config
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mysql.connector import MySQLConnection, errorcode
from utils import decode_jwt_token, extract_user_info_from_payload, get_password_hash

security = HTTPBearer()


def get_db_connection() -> Generator[MySQLConnection]:
    cnx = get_connection(config)
    if not cnx or not cnx.is_connected():
        raise HTTPException(
            status_code=500, detail="데이터베이스 연결에 실패하였습니다."
        )
    try:
        yield cnx  # type: ignore
    finally:
        if cnx and cnx.is_connected():
            cnx.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cnx: MySQLConnection = Depends(get_db_connection),
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


def email_exist(email: str, cnx: Any) -> bool:
    with cnx.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM usr WHERE email = %s", (email,))
        return cursor.fetchone()[0] > 0


def create_user(email: str, password: str, name: str, cnx: Any) -> Optional[int]:
    with cnx.cursor() as cursor:
        hashed_password = get_password_hash(password)
        sql = "INSERT INTO usr (email, pwd, usr_nm) VALUES (%s, %s, %s)"
        try:
            cursor.execute(sql, (email, hashed_password, name))
            cnx.commit()
            return cursor.lastrowid
        except Exception as e:
            print("DB 유저 삽입 에러", e)
            return None


def delete_user(user_id: int, cnx: Any):
    with cnx.cursor() as cursor:
        cursor.execute("DELETE FROM usr WHERE usr_id = %s", (user_id,))
        affected = cursor.rowcount
        cnx.commit()
        if affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="탈퇴할 사용자를 찾을 수 없습니다.",
            )
        return True


def select_user_by_email(email: str, cnx: Any):
    with cnx.cursor() as cursor:
        sql = "SELECT *  FROM usr WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        if row:
            return schemas.UserInDB(
                id=row[0], name=row[1], email=row[2], password=row[3]
            )
        return None


def add_todo_into_database(
    todo: schemas.TodoCreateRequest,
    user_id: int,
    cnx: MySQLConnection,
):
    with cnx.cursor(dictionary=True) as cursor:
        sql = """
            INSERT INTO todo (todo_title, todo_dtl, ctgy, priority_lvl, due_dt, usr_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (
                todo.title,
                todo.description,
                todo.category,
                todo.priority,
                todo.duedate,
                user_id,
            ),
        )
        inserted_id = cursor.lastrowid
    cnx.commit()
    return inserted_id


def get_total_todos_from_datbase(
    user_id: int,
    cnx: Any,
    done: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    with cnx.cursor(dictionary=True) as cursor:
        sql = "SELECT * FROM todo WHERE usr_id = %s"
        params = [user_id]
        if done is not None:
            sql += " AND yn_done = %s"
            params.append(1 if done else 0)
        if category is not None:
            sql += " AND ctgy = %s"
            params.append(category)
        if search is not None and search.strip() != "":
            sql += " AND todo_title LIKE %s"
            params.append(f"%{search}%")
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        if rows:
            return rows


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
