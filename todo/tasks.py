from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from . import models
from . import auth
from .database import db_dependency


router = APIRouter(prefix="/tasks", tags=["tasks"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class CreateTaskRequest(BaseModel):
    text: str
    category_id: int = None
    done: bool = False


class PatchTaskRequest(BaseModel):
    text: str = None
    category_id: int = None
    done: bool = None


class Task(BaseModel):
    id: int
    text: str
    done: bool
    category_id: int | None
    category_name: str | None

    @classmethod
    def from_db(cls, task: models.Task):
        return cls(
            id=task.id,
            text=task.text,
            done=task.done,
            category_id=task.category_id,
            category_name=task.category.name if task.category else None,
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_task(
    user: user_dependency, db: db_dependency, create_task_request: CreateTaskRequest
) -> Task:
    if (
        db.query(models.Category).filter_by(id=create_task_request.category_id).first()
        is None
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"The category with id {create_task_request.category_id} does not exist",
        )

    task = models.Task(
        user_id=user["id"],
        done=create_task_request.done,
        text=create_task_request.done,
        category_id=create_task_request.category_id,
    )
    db.add(task)
    db.commit()

    return Task.from_db(task)


@router.get("/")
def get_tasks(user: user_dependency, db: db_dependency) -> list[Task]:
    tasks = db.query(models.Task).filter_by(user_id=user["id"]).all()

    return [Task.from_db(task) for task in tasks]


@router.get("/{task_id}")
def get_task(user: user_dependency, db: db_dependency, task_id: str = None) -> Task:
    task = db.query(models.Task).filter_by(user_id=user["id"], id=task_id).first()

    if task:
        return Task.from_db(task)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task does not exist")


@router.get("/category/{category_id}")
def get_tasks_by_category(
    user: user_dependency, db: db_dependency, category_id: str = None
) -> list[Task]:
    tasks = (
        db.query(models.Task)
        .filter_by(user_id=user["id"], category_id=category_id)
        .all()
    )
    return [Task.from_db(task) for task in tasks]


@router.patch("/{task_id}")
def edit_task(
    user: user_dependency,
    db: db_dependency,
    task_id: int,
    patch_task_request: PatchTaskRequest,
) -> None:
    task = db.query(models.Task).filter_by(id=task_id, user_id=user["id"]).first()

    if not task:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Task does not exist")

    if patch_task_request.text:
        task.text = patch_task_request.text
    if patch_task_request.done:
        task.done = patch_task_request.done
    if patch_task_request.category_id:
        task.category_id = patch_task_request.category_id

    db.commit()


@router.delete("/{task_id}")
def delete_task(user: user_dependency, db: db_dependency, task_id: str = None) -> None:
    task = db.query(models.Task).filter_by(user_id=user["id"], id=task_id).first()

    if task:
        db.delete(task)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Task does not exist")
