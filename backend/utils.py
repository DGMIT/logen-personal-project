from typing import Union

import bcrypt

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
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
