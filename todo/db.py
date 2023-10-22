from sqlalchemy import StaticPool, create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.engine import URL


from . import models
from . import exceptions


class DataBase:
    def __init__(self):
        url = URL.create(
            "postgresql",
            "postgres",
            "password",
            "0.0.0.0",
            5432,
        )

        self._engine = create_engine(
            url, connect_args={}, poolclass=StaticPool, echo=True
        )
        models.Base.metadata.create_all(self._engine)
        self._session = Session(self._engine)
        pass

    def get_user(self, id: int) -> models.User:
        if user := self._session.query(models.User).filter_by(id=id).first():
            return user
        raise exceptions.UserDoesNotExist()

    def get_user_by_username(self, username: str) -> models.User:
        # # first way
        # conn = self._engine.connect()
        # if user := conn.execute(select(models.User).where(models.User.username == username)).first():
        #     return user

        # second way
        if (
            user := self._session.query(models.User)
            .filter_by(username=username)
            .first()
        ):
            return user

        raise exceptions.UserDoesNotExist()

    def add_user(self, username: str, password_hash: str) -> models.User:
        if (
            self._session.query(models.User)
            .where(models.User.username == username)
            .count()
        ):
            raise exceptions.UserAlreadyExists()

        user = models.User(username=username, password_hash=password_hash)
        self._session.add(user)
        self._session.commit()
        return user

    def remove_user(self, username: str) -> None:
        if (
            user := self._session.query(models.User)
            .filter_by(username=username)
            .first()
        ):
            self._session.delete(user)
            self._session.commit()
        else:
            raise exceptions.UserDoesNotExist()

    def add_task(self, user: models.User, done: bool, text: str) -> models.Task:
        task = models.Task(user=user, done=done, text=text)
        self._session.add(task)
        self._session.commit()
        return task

    def get_tasks(self, user: models.User, ids: list[int] = None) -> list[models.Task]:
        query = self._session.query(models.Task).filter_by(user=user)
        if ids:
            query = query.filter(models.Task.id in ids)
        return query.all()

    def update_task(self, user_id: int, task_id: int, text: str = None, done: bool = None):
        task = self._session.query(models.Task).filter_by(id=task_id, user_id=user_id).first()
        
        if text:
            task.text = text
        
        if done:
            task.done = done
        
        self._session.commit()
