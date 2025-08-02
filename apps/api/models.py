import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class CategoryEnum(str, enum.Enum):
    업무 = "업무"
    개인 = "개인"
    학습 = "학습"
    기타 = "기타"


class PriorityEnum(str, enum.Enum):
    낮음 = "낮음"
    보통 = "보통"
    높음 = "높음"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "usr"
    usr_id: Mapped[int] = mapped_column(primary_key=True)
    usr_nm: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    pwd: Mapped[str] = mapped_column(String(255))
    todos = relationship("Todo", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.usr_id},name={self.usr_nm},email={self.email},pwd={self.pwd})>"


class Todo(Base):
    __tablename__ = "todo"
    todo_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    todo_title: Mapped[str] = mapped_column(String(100), nullable=False)
    todo_dtl: Mapped[str] = mapped_column(Text, nullable=True)
    yn_done: Mapped[bool] = mapped_column(Boolean, default=0)
    ctgy: Mapped[CategoryEnum] = mapped_column(
        Enum(CategoryEnum), default=CategoryEnum.기타
    )
    priority_lvl: Mapped[PriorityEnum] = mapped_column(
        Enum(PriorityEnum), default=PriorityEnum.보통
    )
    due_dt: Mapped[Date] = mapped_column(Date, nullable=False)
    created_dt: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)

    usr_id: Mapped[int] = mapped_column(ForeignKey("usr.usr_id"))
    user = relationship("User", back_populates="todos")

    def __repr__(self) -> str:
        return (
            f"<Todo(id={self.todo_id}, title={self.todo_title}, "
            f"done={self.yn_done}, category={self.ctgy}, priority={self.priority_lvl}, "
            f"due_date={self.due_dt}, user_id={self.usr_id})>"
        )
