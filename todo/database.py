from os import environ
from typing import Annotated
from fastapi import Depends
from sqlalchemy import URL, StaticPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base


url = environ.get("DATABASE_URL") or URL.create(
    "postgresql",
    environ["POSTGRES_USERNAME"],
    environ["POSTGRES_PASSWORD"],
    environ["POSTGRES_HOST"],
    int(environ["POSTGRES_PORT"]),
)

is_sqlite = str(url).startswith("sqlite")
engine = create_engine(
    url,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    **({"poolclass": StaticPool} if is_sqlite else {}),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
