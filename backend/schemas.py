from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from models import Priority, TaskStatus


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    priority: Priority = Priority.medium
    due_date: date | None = None
    tags: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    due_date: date | None = None
    tags: str | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: Priority
    due_date: date | None
    tags: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data: list[TaskOut]
    total: int
