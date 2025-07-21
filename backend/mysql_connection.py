from typing import Any

import mysql.connector
import schemas
from fastapi import HTTPException, status
from mysql.connector import errorcode
from utils import get_password_hash, row_to_dict, rows_to_dict, verify_password


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


def get_connection(config):
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


def get_all_users(cnx: Any):
    with cnx.cursor() as cursor:
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        for row in rows:
            print(row)


def insert_user(email: str, password: str, name: str, cnx: Any) -> bool:
    try:
        with cnx.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM user WHERE email = %s", (email,))
            count = cursor.fetchone()[0]
            if count > 0:
                raise HTTPException(
                    status_code=409, detail="이미 존재하는 이메일입니다."
                )
            hashed_password = get_password_hash(password)
            sql = "INSERT INTO user (email, password, name) VALUES (%s, %s, %s)"
            cursor.execute(sql, (email, hashed_password, name))
            cnx.commit()
        return True
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"디비 오류 :{err}")


def delete_user(user_id, cnx: Any):
    with cnx.cursor() as cursor:
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        cnx.commit()
        return True


def select_user_by_email(email: str, cnx: Any):
    print("select_user_by_email", email, cnx)
    with cnx.cursor() as cursor:
        sql = "SELECT *  fFROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        print("select_user_by_email result", result)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="존재하지 않는 사용자입니다",
            )
        return result


def select_user_by_email_and_password(email: str, password: str, cnx: Any):
    with cnx.cursor() as cursor:
        # 유저 이메일을 통해 디비에서 해당 유저 정보를 가져온다
        _, _, _, find_user_password = select_user_by_email(email, cnx)
        sql = "SELECT * FROM user WHERE email = %s AND password = %s"
        cursor.execute(sql, (email, find_user_password))
        user = cursor.fetchone()
        if not user:
            return None
        if not verify_password(password, find_user_password):
            return None
        return user


def add_todo_into_database(
    todo: schemas.TodoCreateRequest,
    user_id: int,
    cnx: Any,
):
    with cnx.cursor() as cursor:
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


def get_total_todos_from_datbase(user_id, cnx: Any):
    print("user_id", user_id, type(user_id))
    with cnx.cursor() as cursor:
        sql = "SELECT * FROM todo WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        if rows:
            return rows_to_dict(cursor, rows)
    return None


def get_todo_from_database(user_id, todo_id, cnx: Any):
    with cnx.cursor() as cursor:
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        if row:
            return row_to_dict(row)
    return None


def put_todo_from_database(user_id, todo_id, todo, cnx: Any):
    # exclude_unset은 실제로 들어온 필드만 추출하고 싶을때 None 제거용
    update_todo = todo.dict(exclude_unset=True)
    with cnx.cursor(dictionary=True) as cursor:
        set_clause = ", ".join(f"{col} = %s" for col in update_todo.keys())
        sql = f"UPDATE todo SET {set_clause} WHERE user_id = %s AND id = %s"
        values = list(update_todo.values()) + [user_id, todo_id]
        cursor.execute(sql, values)
        cnx.commit()

        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        print("result of row", row)
        if row is None:
            raise HTTPException(
                status_code=500, detail="할일 수정 관련 데이터베이스 오류"
            )
        return row


def delete_todo_from_database(user_id, todo_id, cnx: Any):
    with cnx.cursor() as cursor:
        sql = "DELETE FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        cnx.commit()
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        if row:
            raise HTTPException(
                status_code=500, detail="할일 삭제 관련 데이터베이스 오류"
            )
        return True


def toggle_todo_from_database(user_id, todo_id, cnx: Any):
    with cnx.cursor(dictionary=True) as cursor:
        # 먼저 해당 todo가 존재하는지 확인
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="할일을 찾을 수 없습니다.")

        # 현재 done 상태를 반전시킴
        current_done = row["done"]
        new_done = 0 if current_done else 1

        # done 상태 업데이트
        sql = "UPDATE todo SET done = %s WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (new_done, user_id, todo_id))
        cnx.commit()

        # 업데이트된 todo 정보 반환
        sql = "SELECT * FROM todo WHERE user_id = %s AND id = %s"
        cursor.execute(sql, (user_id, todo_id))
        updated_row = cursor.fetchone()
        return updated_row
