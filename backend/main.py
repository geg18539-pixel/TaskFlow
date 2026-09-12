from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import Base, engine, get_db
from models import Task, TaskStatus, User
from schemas import TaskCreate, TaskOut, TaskPage, TaskUpdate, UserCreate, UserOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="taskflow API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    user = db.scalar(select(User).where(User.username == form_data.username))
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@app.get("/api/tasks", response_model=TaskPage)
def list_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    conditions = [Task.owner_id == current_user.id]

    if search:
        conditions.append(Task.title.like(f"%{search}%"))
    if status_filter is not None:
        conditions.append(Task.status == status_filter)

    total = db.scalar(select(func.count()).select_from(Task).where(*conditions)) or 0

    stmt = (
        select(Task)
        .where(*conditions)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())

    return {"data": items, "total": total}


@app.post("/api/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    task = Task(**payload.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.put("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    task = db.get(Task, task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()
