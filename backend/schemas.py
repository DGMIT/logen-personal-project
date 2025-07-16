from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str


class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    category: Literal["업무", "개인", "학습", "기타"]
    priority: Literal["낮음", "보통", "높음"]
    dueDate: date
    completed: bool = Field(..., alias="completed")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        allow_population_by_field_name = True  # alias 사용 가능하게


class PublicUserInfo(BaseModel):
    id: int
    email: EmailStr
    name: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginData(BaseModel):
    token: str
    user: PublicUserInfo


class UserLoginResponse(BaseModel):
    success: bool
    message: str
    data: UserLoginData


class UserSigninRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserSigninResponse(BaseModel):
    success: bool
    message: str
    data: PublicUserInfo


class UserLogoutResponse(BaseModel):
    success: bool
    message: str


class UserWithdrawResponse(BaseModel):
    success: bool
    message: str


class UserMeResponse(BaseModel):
    success: bool
    message: str
    data: PublicUserInfo


class TodoCreateData(BaseModel):
    todo: TodoItem


class TodoCreateRequest(BaseModel):
    description: str
    category: Literal["업무", "개인", "학습", "기타"]
    dueDate: date
    priority: Literal["낮음", "보통", "높음"]


class TodoCreateResponse(BaseModel):
    success: bool
    message: str
    data: TodoCreateData


class TodoResponse(BaseModel):
    success: bool
    message: str
    data: TodoCreateData


class TodoListQueryParams(BaseModel):
    completed: Optional[bool] = Field(None, description="완료 여부 필터링")
    category: Optional[Literal["업무", "개인", "학습", "기타"]] = Field(
        None, description="카테고리 필터링"
    )
    priority: Optional[Literal["높음", "보통", "낮음"]] = Field(
        None, description="우선순위 필터링"
    )
    sort: Optional[Literal["createdAt", "dueDate", "priority"]] = Field(
        "createdAt", description="정렬 기준"
    )
    order: Optional[Literal["asc", "desc"]] = Field("desc", description="정렬 방향")
    page: Optional[int] = Field(1, description="페이지 번호")
    limit: Optional[int] = Field(10, description="페이지당 항목 수")


class PaginationMeta(BaseModel):
    current_page: int = Field(..., alias="currentPage")
    total_pages: int = Field(..., alias="totalPages")
    total_items: int = Field(..., alias="totalItems")

    class Config:
        allow_population_by_field_name = True


class TodoListData(BaseModel):
    todos: List[TodoItem]
    pagination: PaginationMeta


class TodoListResponse(BaseModel):
    success: bool
    message: str
    data: TodoListData


class TodoPathParams(BaseModel):
    id: int


class TodoUpdateRequest(BaseModel):
    title: Optional[str]
    description: Optional[str]
    category: Optional[Literal["업무", "학습", "개인"]]
    due_date: Optional[date]
    priority: Optional[Literal["높음", "보통", "낮음"]]
    completed: Optional[bool]

    class Config:
        allow_population_by_field_name = True
        fields = {
            "due_date": "dueDate",
        }


class TodoUpdateData(BaseModel):
    todo: TodoItem


class TodoUpdateResponse(BaseModel):
    success: bool
    message: str
    data: TodoUpdateData


class TodoDeletePathParams(BaseModel):
    id: int  # 삭제할 할일 ID


class DeleteSuccessResponse(BaseModel):
    success: bool = True
    message: str = "할일이 성공적으로 삭제되었습니다"


class ErrorResponse(BaseModel):
    success: bool = False
    message: str


class TodoTogglePathParams(BaseModel):
    id: int  # 완료 상태를 변경할 할일 ID


class ToggleSuccessResponse(BaseModel):
    success: bool = True
    message: str = "완료 상태가 변경되었습니다"
