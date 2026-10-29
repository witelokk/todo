from fastapi import Depends, FastAPI
from importlib.metadata import version
from sqlalchemy.orm import Session

from . import auth, tasks, categories
from .database import SessionLocal, engine, Base


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Todo API", version=version("todo"))
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(categories.router)

Base.metadata.create_all(bind=engine)
