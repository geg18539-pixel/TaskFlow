import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class TaskStatus(str, enum.Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.todo, nullable=False
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority), default=Priority.medium, nullable=False
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="tasks")
