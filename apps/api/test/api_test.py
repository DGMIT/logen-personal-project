from unittest.mock import MagicMock

import database as db  # get_current_user, get_db_connection이 정의된 곳
import schemas
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def override_get_current_user():
    return schemas.PublicUser(id=1, email="ceh20002@naver.com", name="testuser")


def override_get_db_connection():
    return MagicMock()


app.dependency_overrides[db.get_current_user] = override_get_current_user
app.dependency_overrides[db.get_db_connection] = override_get_db_connection


def test_get_todos():
    response = client.get("/todos")
    print("response", response)
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "할일 목록조회 성공"
    assert type(schemas.TodoListData(**response.json()["data"])) == schemas.TodoListData
