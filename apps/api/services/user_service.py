import database as db
import schemas
from fastapi import Depends, HTTPException, status
from mysql.connector.connection import MySQLConnection
from utils import verify_password


def login_service(
    email: str, password: str, cnx: MySQLConnection = Depends(db.get_db_connection)
):
    user = db.select_user_by_email(email, cnx)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="해당 사용자를 찾을 수 없습니다.",
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 올바르지 않습니다. 다시 확인해 주세요.",
        )
    return schemas.PublicUser(id=user.id, email=user.email, name=user.name)


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
