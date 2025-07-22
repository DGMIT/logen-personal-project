import os
import requests
from typing import Optional, Dict, Any

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".token")

# --- JWT 토큰 관리 ---
def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token() -> Optional[str]:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def auth_headers() -> Dict[str, str]:
    token = load_token()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

# --- API 함수들 ---

def register(email: str, password: str, name: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/register"
    resp = requests.post(url, json={"email": email, "password": password, "name": name})
    return resp.json()

def login(email: str, password: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/login"
    resp = requests.post(url, json={"email": email, "password": password})
    data = resp.json()
    if resp.ok and data.get("success") and "data" in data and "token" in data["data"]:
        save_token(data["data"]["token"])
    return data

def logout() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/logout"
    headers = auth_headers()
    resp = requests.post(url, headers=headers)
    clear_token()
    return resp.json()

def withdraw() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/withdraw"
    headers = auth_headers()
    resp = requests.post(url, headers=headers)
    clear_token()
    return resp.json()

def get_me() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/user"
    headers = auth_headers()
    resp = requests.get(url, headers=headers)
    return resp.json()

# --- 할일 API ---
def create_todo(title: str, description: str, category: str, duedate: str, priority: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/todos"
    headers = auth_headers()
    payload = {
        "title": title,
        "description": description,
        "category": category,
        "duedate": duedate,
        "priority": priority
    }
    resp = requests.post(url, json=payload, headers=headers)
    return resp.json()

def get_todo(todo_id: int) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/todos/{todo_id}"
    headers = auth_headers()
    resp = requests.get(url, headers=headers)
    return resp.json()

def list_todos(
    done: Optional[bool] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    page: int = 1,
    limit: int = 10
) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/todos"
    headers = auth_headers()
    params = {"page": page, "limit": limit}
    if done is not None:
        params["done"] = str(done).lower()
    if category:
        params["category"] = category
    if priority:
        params["priority"] = priority
    if sort:
        params["sort"] = sort
    if order:
        params["order"] = order
    resp = requests.get(url, headers=headers, params=params)
    return resp.json()

def update_todo(
    todo_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    duedate: Optional[str] = None,
    priority: Optional[str] = None,
    done: Optional[bool] = None
) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/todos/{todo_id}"
    headers = auth_headers()
    payload = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if category is not None:
        payload["category"] = category
    if duedate is not None:
        payload["duedate"] = duedate
    if priority is not None:
        payload["priority"] = priority
    if done is not None:
        payload["done"] = done
    resp = requests.put(url, json=payload, headers=headers)
    return resp.json()

def delete_todo(todo_id: int) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/todos/{todo_id}"
    headers = auth_headers()
    resp = requests.delete(url, headers=headers)
    return resp.json()

def toggle_todo(todo_id: int) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/todos/{todo_id}/toggle"
    headers = auth_headers()
    resp = requests.patch(url, headers=headers)
    return resp.json()
