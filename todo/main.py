from hashlib import md5
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy import URL, create_engine, StaticPool
from sqlalchemy.orm import Session

from . import models


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

db_url = URL.create(
    "postgresql",
    "postgres",
    "password",
    "0.0.0.0",
    5432,
)

db_engine = create_engine(db_url, connect_args={}, poolclass=StaticPool, echo=True)
models.Base.metadata.create_all(db_engine)


def hash_password(password: str) -> str:
    return md5(password.encode()).hexdigest()


@app.post("/user", status_code=status.HTTP_201_CREATED)
def user(username: str, password: str):
    with Session(db_engine) as session:
        if session.query(models.User).where(models.User.username == username).count():
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"User with username {username} already exists",
            )

        user = models.User(username=username, password_hash=hash_password(password))
        session.add(user)
        session.commit()


@app.get("/user")
def user(username: str, password: str):
    with Session(db_engine) as session:
        user = session.query(models.User).filter_by(username=username).first()

    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"User with username {username} does not exists"
        )

    if user.password_hash == hash_password(password):
        return jwt.encode({"id": user.id}, "secret")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Incorrect password")


@app.delete("/user")
def user(username: str):
    with Session(db_engine) as session:
        user = db_engine.query(models.User).filter_by(username=username).first()

        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"User with username {username} does not exists",
            )

        session.delete(user)
        session.commit()


@app.post("/task", status_code=status.HTTP_201_CREATED)
def add_task(
    token: Annotated[str, Depends(oauth2_scheme)],
    text: str,
    done: bool = False,
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        task = models.Task(user_id=jwt_payload["id"], done=done, text=text)
        session.add(task)
        session.commit()

        return {
            "id": task.id,
        }


@app.get("/task")
def get_tasks(token: Annotated[str, Depends(oauth2_scheme)]):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        tasks = session.query(models.Task).filter_by(user_id=jwt_payload["id"]).all()

    return tasks


@app.get("/task/{task_id}")
def get_tasks(token: Annotated[str, Depends(oauth2_scheme)], task_id: str = None):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        task = (
            session.query(models.Task)
            .filter_by(user_id=jwt_payload["id"], id=task_id)
            .first()
        )

    if task:
        return task
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task does not exist")


@app.patch("/task/{task_id}")
def edit_task(
    token: Annotated[str, Depends(oauth2_scheme)],
    task_id: int,
    text: str = None,
    done: bool = None,
    category_id: int = None,
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        task = (
            session.query(models.Task)
            .filter_by(id=task_id, user_id=jwt_payload["id"])
            .first()
        )

        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Task does not exist")

        if text:
            task.text = text
        if done:
            task.done = done
        if category_id:
            task.category_id = category_id

        session.commit()


@app.delete("/task/{task_id}")
def delete_task(token: Annotated[str, Depends(oauth2_scheme)], task_id: str = None):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        task = (
            session.query(models.Task)
            .filter_by(user_id=jwt_payload["id"], id=task_id)
            .first()
        )

        if task:
            session.delete(task)
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Task does not exist")


@app.post("/category")
def add_category(
    token: Annotated[str, Depends(oauth2_scheme)],
    name: str,
    status_code=status.HTTP_201_CREATED,
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        category = models.Category(user_id=jwt_payload["id"], name=name)
        session.add(category)
        session.commit()

        return {"id": category.id}


@app.get("/category")
def get_categories(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        categories = (
            session.query(models.Category).filter_by(user_id=jwt_payload["id"]).all()
        )
        return categories


@app.get("/category/{category_id}")
def delete_category(token: Annotated[str, Depends(oauth2_scheme)], category_id: int):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        category = (
            session.query(models.Category)
            .filter_by(user_id=jwt_payload["id"], id=category_id)
            .first()
        )

        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category is not found")

        return category


@app.patch("/category/{category_id}")
def delete_category(
    token: Annotated[str, Depends(oauth2_scheme)], category_id: int, name: str
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        category = (
            session.query(models.Category)
            .filter_by(user_id=jwt_payload["id"], id=category_id)
            .first()
        )

        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category is not found")

        category.name = name

        session.commit()


@app.delete("/category/{category_id}")
def delete_category(
    token: Annotated[str, Depends(oauth2_scheme)],
    category_id: int,
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    with Session(db_engine) as session:
        category = (
            session.query(models.Category)
            .filter_by(user_id=jwt_payload["id"], id=category_id)
            .first()
        )

        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category is not found")

        session.delete(category)
        session.commit()
