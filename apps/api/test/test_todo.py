from typing import Any
from unittest.mock import MagicMock

import database as db
import schemas
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_todos():
    def override_get_current_user():
        return schemas.PublicUser(id=1, email="ceh20002@naver.com", name="testuser")

    def override_get_db_connection():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "todo_id": 1,
            "todo_title": "테스트 할일",
            "todo_dtl": "테스트 내용",
            "yn_done": False,
            "due_dt": "2025-07-31T00:00:00",
            "usr_id": 1,
            "ctgy": "개인",
            "priority_lvl": "낮음",
            "created_dt": "2025-07-01T00:00:00",
        }

        mock_cursor.rowcount = 1  # put/delete 성공한 척

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        return mock_conn

    app.dependency_overrides[db.get_current_user] = override_get_current_user
    app.dependency_overrides[db.get_db_connection] = override_get_db_connection

    response = client.get("/todos")
    print("response", response)
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "할일 목록조회 성공"
    assert type(schemas.TodoListData(**response.json()["data"])) == schemas.TodoListData

    app.dependency_overrides.clear()


def test_get_todo():

    def override_get_current_user():
        return schemas.PublicUser(id=1, email="ceh20002@naver.com", name="testuser")

    def override_get_db_connection():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "todo_id": 1,
            "todo_title": "테스트 할일",
            "todo_dtl": "테스트 내용",
            "yn_done": False,
            "due_dt": "2025-07-31T00:00:00",
            "usr_id": 1,
            "ctgy": "개인",
            "priority_lvl": "낮음",
            "created_dt": "2025-07-01T00:00:00",
        }

        mock_cursor.rowcount = 1  # put/delete 성공한 척

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        return mock_conn

    app.dependency_overrides[db.get_current_user] = override_get_current_user
    app.dependency_overrides[db.get_db_connection] = override_get_db_connection
    todo_id = 1
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == f"{todo_id}번째 할일 조회 성공"
    assert type(schemas.Todo(**response.json()["data"])) == schemas.Todo

    app.dependency_overrides.clear()


def test_update_todo():

    def override_get_current_user():
        return schemas.PublicUser(id=1, email="ceh20002@naver.com", name="testuser")

    def override_get_db_connection():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "todo_id": 1,
            "todo_title": "테스트 할일",
            "todo_dtl": "테스트 내용",
            "yn_done": False,
            "due_dt": "2025-07-31T00:00:00",
            "usr_id": 1,
            "ctgy": "개인",
            "priority_lvl": "낮음",
            "created_dt": "2025-07-01T00:00:00",
        }

        mock_cursor.rowcount = 1  # put/delete 성공한 척

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        return mock_conn

    app.dependency_overrides[db.get_current_user] = override_get_current_user
    app.dependency_overrides[db.get_db_connection] = override_get_db_connection

    todo_id = 1
    update_data: dict[str, Any] = {
        "title": "수정된 제목",
        "description": "수정된 내용",
        "done": True,
        "duedate": "2025-08-01T00:00:00",
        "category": "업무",
        "priority": "보통",
    }

    response = client.put(f"/todos/{todo_id}", json=update_data)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "수정 성공"
    app.dependency_overrides.clear()


def test_delete_todo():
    def override_get_current_user():
        return schemas.PublicUser(id=1, email="ceh20002@naver.com", name="testuser")

    def override_get_db_connection():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "todo_id": 1,
            "todo_title": "테스트 할일",
            "todo_dtl": "테스트 내용",
            "yn_done": False,
            "due_dt": "2025-07-31T00:00:00",
            "usr_id": 1,
            "ctgy": "개인",
            "priority_lvl": "낮음",
            "created_dt": "2025-07-01T00:00:00",
        }

        mock_cursor.rowcount = 1  # put/delete 성공한 척

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        return mock_conn

    app.dependency_overrides[db.get_current_user] = override_get_current_user
    app.dependency_overrides[db.get_db_connection] = override_get_db_connection
    todo_id = 1

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == f"{todo_id}번째 할일 삭제 성공"
    app.dependency_overrides.clear()
