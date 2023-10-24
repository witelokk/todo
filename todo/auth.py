from datetime import datetime, timedelta, UTC
import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models
from .database import db_dependency


router = APIRouter(prefix="/auth", tags=["auth"])


SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    if db.query(models.User).filter_by(username=create_user_request.username).count():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"A user with the username {create_user_request.username} already exists",
        )

    user = models.User(
        username=create_user_request.username,
        password_hash=bcrypt_context.hash(create_user_request.password),
    )

    db.add(user)
    db.commit()


@router.post("/token")
def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User does not exist")

    return jwt.encode(
        {
            "username": form_data.username,
            "id": user.id,
            "expire": (datetime.now(UTC) + timedelta(minutes=60)).timestamp(),
        },
        SECRET_KEY,
        ALGORITHM,
    )


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(models.User).filter_by(username=username).first()

    if not user:
        return None

    if not bcrypt_context.verify(password, user.password_hash):
        return None

    return user


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload["username"]
        user_id = payload["id"]
        expire = payload["expire"]
    except (jwt.DecodeError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    if datetime.now(UTC).timestamp() > expire:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "The token has expired")

    return {"username": username, "id": user_id}
