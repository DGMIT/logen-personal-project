import datetime
from typing import Union

import bcrypt
import jwt
from config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
from fastapi import HTTPException

columns: list[str] = [
    "id",
    "title",
    "description",
    "done",
    "category",
    "priority",
    "duedate",
    "created_at",
    "user_id",
]


def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def row_to_dict(rows: tuple[Union[str, int]]) -> dict[str, Union[str, int]]:
    return dict(zip(columns, rows))


def rows_to_dict(cursor, rows) -> list[dict[str, Union[str, int]]]:
    print(rows)
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def create_access_token(
    data: dict[str, str], expires_delta: datetime.timedelta | None = None
):
    if not JWT_SECRET_KEY or not JWT_ACCESS_TOKEN_EXPIRE_MINUTES or not JWT_ALGORITHM:
        raise HTTPException(status_code=500, detail="JWT 설정이 올바르지 않습니다.")

    to_encode: dict[str, str] = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str):
    if not JWT_SECRET_KEY or not JWT_ACCESS_TOKEN_EXPIRE_MINUTES or not JWT_ALGORITHM:
        raise HTTPException(status_code=500, detail="JWT 설정이 올바르지 않습니다.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")


def extract_user_info_from_payload(payload: dict):
    user_id = payload.get("sub")
    user_email = payload.get("email")
    if not user_id or not user_email:
        raise HTTPException(status_code=401, detail="토큰에 필요한 정보가 없습니다.")
    return user_id, user_email
