from hashlib import md5
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from .db import DataBase
from . import exceptions


app = FastAPI()
db = DataBase()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    return md5(password.encode()).hexdigest()


@app.post("/user")
def user(username: str, password: str, status_code=status.HTTP_201_CREATED):
    try:
        user = db.add_user(username, hash_password(password))
        return jwt.encode({"id": user.id}, "secret")
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"User with username {username} already exists"
        )


@app.get("/user")
def user(username: str, password: str):
    try:
        user = db.get_user_by_username(username)
    except exceptions.UserDoesNotExist:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"User with username {username} does not exists"
        )

    if user.password_hash == hash_password(password):
        return jwt.encode({"id": user.id}, "secret")
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Incorrect password")


@app.delete("/user")
def user(username: str):
    try:
        db.remove_user(username)
    except exceptions.UserDoesNotExist:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"User with username {username} does not exists"
        )


@app.post("/task")
def add_task(
    token: Annotated[str, Depends(oauth2_scheme)],
    text: str,
    done: bool = False,
    status_code=status.HTTP_201_CREATED,
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])

    user = db.get_user(jwt_payload["id"])
    task = db.add_task(user, done, text)

    return {"task_id": task.id}


@app.get("/task")
def get_tasks(
    token: Annotated[str, Depends(oauth2_scheme)], task_ids: list[str] = None
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])
    user = db.get_user(jwt_payload["id"])

    return db.get_tasks(user, task_ids)


@app.patch("/task")
def edit_task(
    token: Annotated[str, Depends(oauth2_scheme)],
    task_id: int,
    text: str = None,
    done: bool = None,
):
    jwt_payload = jwt.decode(token, "secret", ["HS256"])
    user_id = jwt_payload["id"]

    db.update_task(user_id, task_id, text, done)
