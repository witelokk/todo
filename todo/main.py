from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import models, auth
from .database import SessionLocal, engine, Base


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


app = FastAPI()
app.include_router(auth.router)

Base.metadata.create_all(bind=engine)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(auth.get_current_user)]


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def add_task(
    user: user_dependency,
    db: db_dependency,
    text: str,
    done: bool = False,
):
    task = models.Task(user_id=user["id"], done=done, text=text)
    db.add(task)
    db.commit()

    return {
        "id": task.id,
    }


@app.get("/tasks")
def get_tasks(user: user_dependency, db: db_dependency):
    tasks = db.query(models.Task).filter_by(user_id=user["id"]).all()

    return tasks


@app.get("/tasks/{task_id}")
def get_tasks(user: user_dependency, db: db_dependency, task_id: str = None):
    task = db.query(models.Task).filter_by(user_id=user["id"], id=task_id).first()

    if task:
        return task
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task does not exist")


@app.patch("/task/{task_id}")
def edit_task(
    user: user_dependency,
    db: db_dependency,
    task_id: int,
    text: str = None,
    done: bool = None,
    category_id: int = None,
):
    task = db.query(models.Task).filter_by(id=task_id, user_id=user["id"]).first()

    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task does not exist")

    if text:
        task.text = text
    if done:
        task.done = done
    if category_id:
        task.category_id = category_id

    db.commit()


@app.delete("/tasks/{task_id}")
def delete_task(user: user_dependency, db: db_dependency, task_id: str = None):
    task = db.query(models.Task).filter_by(user_id=user["id"], id=task_id).first()

    if task:
        db.delete(task)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task does not exist")


@app.post("/categories")
def add_category(
    user: user_dependency,
    db: db_dependency,
    name: str,
    status_code=status.HTTP_201_CREATED,
):
    category = models.Category(user_id=user["id"], name=name)
    db.add(category)
    db.commit()

    return {"id": category.id}


@app.get("/categories")
def get_categories(user: user_dependency, db: db_dependency):
    categories = db.query(models.Category).filter_by(user_id=user["id"]).all()
    return categories


@app.get("/categories/{category_id}")
def delete_category(user: user_dependency, db: db_dependency, category_id: int):
    category = (
        db.query(models.Category).filter_by(user_id=user["id"], id=category_id).first()
    )

    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category is not found")

    return category


@app.patch("/categories/{category_id}")
def delete_category(
    user: user_dependency, db: db_dependency, category_id: int, name: str
):
    category = (
        db.query(models.Category).filter_by(user_id=user["id"], id=category_id).first()
    )

    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category is not found")

    category.name = name

    db.commit()


@app.delete("/categories/{category_id}")
def delete_category(
    user: user_dependency,
    db: db_dependency,
    category_id: int,
):
    category = (
        db.query(models.Category).filter_by(user_id=user["id"], id=category_id).first()
    )

    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category is not found")

    db.delete(category)
    db.commit()
