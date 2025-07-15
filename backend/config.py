import os

from dotenv import load_dotenv

load_dotenv()  # .env 파일 읽어서 환경변수로 등록

config = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "todo_app"),
    "raise_on_warnings": True,
}
