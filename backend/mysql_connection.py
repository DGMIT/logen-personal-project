from typing import Any, Generator, Optional

import mysql.connector
import schemas
from config import config
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mysql.connector import MySQLConnection, errorcode
from utils import (
    decode_jwt_token,
    extract_user_info_from_payload,
    get_password_hash,
    rows_to_dict,
    verify_password,
)

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
    token = credentials.credentials
    payload = decode_jwt_token(token)
    _, user_email = extract_user_info_from_payload(payload)
    user = select_user_by_email(user_email, cnx)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다. 다시 로그인해 주세요.",
        )
    return schemas.PublicUser(id=user[0], email=user[2], name=user[1])


# database.py
def ensure_tables_exist(cnx: Any):
    cursor = cnx.cursor()
    cursor.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name IN ('user', 'todo');
    """
    )
    existing_tables = {row[0] for row in cursor.fetchall()}

    if "user" not in existing_tables:
        cursor.execute(
            """
            CREATE TABLE user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
        """
        )

    if "todo" not in existing_tables:
        cursor.execute(
            """
            CREATE TABLE todo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                done TINYINT(1) DEFAULT 0,
                category ENUM('업무', '개인', '학습', '기타') DEFAULT '기타',
                priority ENUM('낮음', '보통', '높음') DEFAULT '보통',
                duedate DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
            );
        """
        )
        # 인덱스 생성
        cursor.execute("CREATE INDEX idx_todo_user_id ON todo(user_id);")
        cursor.execute("CREATE INDEX idx_todo_duedate ON todo(duedate);")
        cursor.execute("CREATE INDEX idx_todo_done ON todo(done);")
        cursor.execute(
            "CREATE INDEX idx_todo_user_priority ON todo(user_id, priority);"
        )

    cnx.commit()
    cursor.close()


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


def insert_user(email: str, password: str, name: str, cnx: Any) -> bool:
    with cnx.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM user WHERE email = %s", (email,))
        count = cursor.fetchone()[0]
        if count > 0:
            return False
        hashed_password = get_password_hash(password)
        sql = "INSERT INTO user (email, password, name) VALUES (%s, %s, %s)"
        cursor.execute(sql, (email, hashed_password, name))
        user_id = cursor.lastrowid
        cnx.commit()
    return user_id


def delete_user(user_id: int, cnx: Any):
    with cnx.cursor() as cursor:
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
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
        sql = "SELECT *  FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="해당 사용자를 찾을 수 없습니다.",
            )
        return result


def select_user_by_email_and_password(email: str, password: str, cnx: Any):
    user_id, user_name, user_email, user_password = select_user_by_email(email, cnx)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="해당 사용자를 찾을 수 없습니다.",
        )
    if not verify_password(password, user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 올바르지 않습니다. 다시 확인해 주세요.",
        )
    return user_id, user_name, user_email


def add_todo_into_database(
    todo: schemas.TodoCreateRequest,
    user_id: int,
    cnx: MySQLConnection,
):
    with cnx.cursor(dictionary=True) as cursor:
        sql = """
            INSERT INTO todo (title, description, category, priority, duedate, user_id)
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


def get_total_todos_from_datbase(user_id: int, cnx: Any, done: Optional[bool] = None, category: Optional[str] = None, search: Optional[str] = None):
    with cnx.cursor(dictionary=True) as cursor:
        sql = "SELECT * FROM todo WHERE user_id = %s"
        params = [user_id]
        if done is not None:
            sql += " AND done = %s"
            params.append(1 if done else 0)
        if category is not None:
            sql += " AND category = %s"
            params.append(category)
        if search is not None and search.strip() != "":
            sql += " AND title LIKE %s"
            params.append(f"%{search}%")
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        if rows:
            return rows


def get_todo_from_database(user_id: int, todo_id: int, cnx: MySQLConnection):
    with cnx.cursor(dictionary=True) as cursor:
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        if row:
            return row


def put_todo_from_database(
    user_id: int, todo_id: int, todo: schemas.TodoUpdateRequest, cnx: MySQLConnection
):
    update_todo = todo.model_dump(exclude_unset=True)
    with cnx.cursor(dictionary=True) as cursor:
        set_clause = ", ".join(f"{col} = %s" for col in update_todo.keys())
        sql = f"UPDATE todo SET {set_clause} WHERE user_id = %s AND id = %s"
        values = list(update_todo.values()) + [user_id, todo_id]
        cursor.execute(sql, values)
        cnx.commit()

        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        return row


def delete_todo_from_database(user_id: int, todo_id: int, cnx: Any):
    with cnx.cursor() as cursor:
        sql = "DELETE FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        cnx.commit()
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        if row:
            raise HTTPException(
                status_code=500,
                detail="할일 삭제에 실패하였습니다. 다시 시도해 주세요.",
            )
        return True


def toggle_todo_from_database(user_id: int, todo_id: int, cnx: Any):
    with cnx.cursor(dictionary=True) as cursor:
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="해당 할일을 찾을 수 없습니다.")
        current_done = row["done"]
        new_done = 0 if current_done else 1
        sql = "UPDATE todo SET done = %s WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (new_done, user_id, todo_id))
        cnx.commit()
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        updated_row = cursor.fetchone()
        return updated_row
