import database as db
import schemas
from fastapi import Depends, HTTPException, status
from mysql.connector.connection import MySQLConnection


def login_service(
    email: str, password: str, cnx: MySQLConnection = Depends(db.get_db_connection)
):
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="이메일을 입력해주세요."
        )
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호를 입력해주세요",
        )
    user_id, user_email, user_name = db.select_user_by_email_and_password(
        email, password, cnx
    )
    if not user_id or not user_email or not user_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 유저입니다.",
        )
    return user_id, user_email, user_name
