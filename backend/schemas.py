from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    # password 필드는 DB 모델에서만 사용, API 응답에는 포함하지 않음


class UserInDB(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str


class Todo(BaseModel):
    id: int
    title: str
    description: str
    category: Literal["업무", "개인", "학습", "기타"]
    priority: Literal["낮음", "보통", "높음"]
    duedate: date
    done: bool
    created_at: datetime


class PublicUser(BaseModel):
    id: int
    email: EmailStr
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginData(BaseModel):
    token: str
    user: PublicUser


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: LoginData


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: PublicUser


class LogoutResponse(BaseModel):
    success: bool
    message: str


class WithdrawResponse(BaseModel):
    success: bool
    message: str


class MeResponse(BaseModel):
    success: bool
    message: str
    data: PublicUser


class TodoCreateRequest(BaseModel):
    title: str
    description: str
    category: Literal["업무", "개인", "학습", "기타"]
    duedate: date
    priority: Literal["낮음", "보통", "높음"]


class TodoCreateResponse(BaseModel):
    success: bool
    message: str
    data: Todo


class TodoResponse(BaseModel):
    success: bool
    message: str
    data: Todo


class PaginationMeta(BaseModel):
    current_page: int = Field(..., alias="currentPage")
    total_pages: int = Field(..., alias="totalPages")
    total_items: int = Field(..., alias="totalItems")

    class Config:
        allow_population_by_field_name = True


class TodoListData(BaseModel):
    todos: List[Todo]
    pagination: PaginationMeta


class TodoListResponse(BaseModel):
    success: bool
    message: str
    data: TodoListData


class TodoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Literal["업무", "학습", "개인", "기타"]] = None
    duedate: Optional[date] = None
    priority: Optional[Literal["높음", "보통", "낮음"]] = None
    done: Optional[bool] = None


class TodoUpdateResponse(BaseModel):
    success: bool
    message: str
    data: TodoUpdateRequest


class DeleteResponse(BaseModel):
    success: bool = True
    message: str = "할일이 성공적으로 삭제되었습니다"


class ErrorResponse(BaseModel):
    success: bool = False
    message: str


class ToggleResponse(BaseModel):
    success: bool = True
    message: str = "완료 상태가 변경되었습니다"
