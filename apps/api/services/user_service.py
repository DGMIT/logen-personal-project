import database as db
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
    user = db.select_user_by_email_and_password(email, password, cnx)
    if not user.id or not user.email or not user.name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 유저입니다.",
        )
    return user


def register_service(
    email: str,
    password: str,
    name: str,
    cnx: MySQLConnection = Depends(db.get_db_connection),
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
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="이름을 입력해주세요"
        )
    user_id = db.insert_user(email, password, name, cnx)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 이메일입니다.",
        )
    return user_id
