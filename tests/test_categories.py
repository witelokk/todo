from datetime import UTC, datetime, timedelta
from os import environ
from fastapi import status
from fastapi.testclient import TestClient
import jwt
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from todo import models
from todo.database import get_db, Base
from todo.main import app



engine = create_engine(
    "sqlite:///",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db



def setup_function() -> None:
    Base.metadata.create_all(bind=engine)

    with TestSessionLocal() as db:
        user1 = models.User(username="test1", password_hash="")
        user2 = models.User(username="test2", password_hash="")
        db.add_all((user1, user2))
        category_1 = models.Category(name="Category1", user=user1)
        category_2 = models.Category(name="Category2", user=user2)
        category_3 = models.Category(name="Category3", user=user2)
        db.add_all((category_1, category_2, category_3))
        db.commit()


def teardown_function() -> None:
    Base.metadata.drop_all(bind=engine)


def mock_jwt_token(username: str, id: int) -> str:
    return jwt.encode(
        {
            "username": username,
            "id": id,
            "expire": (datetime.now(UTC) + timedelta(minutes=60)).timestamp(),
        },
        environ["SECRET_KEY"],
        "HS256",
    )


def test_get_categories_user1(client: TestClient):
    response = client.get(
        "/categories", headers={"Authorization": f"Bearer {mock_jwt_token('test1', 1)}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["name"] == "Category1"


def test_get_category_user1(client: TestClient):
    response = client.get(
        "/categories/1",
        headers={"Authorization": f"Bearer {mock_jwt_token('test1', 1)}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Category1"


def test_get_category_user1_without_access(client: TestClient):
    response = client.get(
        "/categories/2",
        headers={"Authorization": f"Bearer {mock_jwt_token('test1', 1)}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_categories_user2(client: TestClient):
    response = client.get(
        "/categories", headers={"Authorization": f"Bearer {mock_jwt_token('test2', 2)}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == 2
    assert response.json()[0]["name"] == "Category2"
    assert response.json()[1]["id"] == 3
    assert response.json()[1]["name"] == "Category3"


def test_add_category(client: TestClient):
    response = client.post(
        "/categories",
        headers={"Authorization": f"Bearer {mock_jwt_token('test2', 2)}"},
        json={"name": "Category4"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 4
    assert response.json()["name"] == "Category4"


def test_edit_category(client: TestClient):
    response = client.patch(
        "/categories/1",
        headers={"Authorization": f"Bearer {mock_jwt_token('test2', 1)}"},
        json={"name": "Test"},
    )

    assert response.status_code == status.HTTP_200_OK

    with TestSessionLocal() as db:
        category = db.query(models.Category).filter_by(id=1).first()
        assert category.name == "Test"


def test_delete_category(client: TestClient):
    response = client.delete(
        "/categories/1",
        headers={"Authorization": f"Bearer {mock_jwt_token('test2', 1)}"},
    )

    assert response.status_code == status.HTTP_200_OK

    with TestSessionLocal() as db:
        category = db.query(models.Category).filter_by(id=1).first()
        assert category == None
