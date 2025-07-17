from datetime import date
from typing import Any

import mysql.connector
import schemas
from fastapi import HTTPException
from mysql.connector import errorcode
from utils import get_password_hash, verify_password


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
    print(config)
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


def insert_user(email: str, password: str, name: str, cnx: Any):
    with cnx.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM user WHERE email = %s", (email,))
        count = cursor.fetchone()[0]
        if count > 0:
            raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")
        hashed_password = get_password_hash(password)
        sql = "INSERT INTO user (email, password, name) VALUES (%s, %s, %s)"
        cursor.execute(sql, (email, hashed_password, name))
        cnx.commit()
    return True


def delete_user(user_id, cnx: Any):
    with cnx.cursor() as cursor:
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        cnx.commit()
        return True


def select_user_by_email(email, cnx: Any):
    print(email)
    with cnx.cursor() as cursor:
        sql = "SELECT * FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        print("result", result)
        return result


def select_user_by_email_and_password(email, password, cnx: Any):
    with cnx.cursor() as cursor:
        # 유저 이메일을 통해 디비에서 해당 유저 정보를 가져온다
        user = select_user_by_email(email, cnx)
        _, _, _, find_user_password = select_user_by_email(email, cnx)
        sql = "SELECT * FROM user WHERE email = %s AND password = %s"
        cursor.execute(sql, (email, find_user_password))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="존재하지 않는 이메일입니다.")
        if not verify_password(password, find_user_password):
            raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
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
                todo.due_date,
                user_id,
            ),
        )
    cnx.commit()
