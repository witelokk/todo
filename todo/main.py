from hashlib import md5

from fastapi import FastAPI, HTTPException, Response
import jwt

from .db import DataBase
from . import exceptions


app = FastAPI()
db = DataBase()


def hash_password(password: str) -> str:
    return md5(password.encode()).hexdigest()


@app.post("/user")
def user(username: str, password: str):
    try:
        user = db.add_user(username, hash_password(password))
        return jwt.encode({"id": user.id}, "secret")
    except exceptions.UserAlreadyExists:
        raise HTTPException(409, f"User with username {username} already exists")


@app.get("/user")
def user(username: str, password: str):
    try:
        user = db.get_user_by_username(username)
    except exceptions.UserDoesNotExist:
        raise HTTPException(404, f"User with username {username} does not exists")

    if user.password_hash == hash_password(password):
        return jwt.encode({"id": user.id}, "secret")
    else:
        raise HTTPException(401, f"Incorrect password")


@app.delete("/user")
def user(username: str):
    try:
        db.remove_user(username)
    except exceptions.UserDoesNotExist:
        raise HTTPException(404, f"User with username {username} does not exists")
