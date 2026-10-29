"""Regression tests for task creation and category ownership."""
from fastapi.testclient import TestClient

from tests.test_categories import (
    mock_jwt_token,
    setup_function,
    teardown_function,
    TestSessionLocal,
)
from todo import models


def headers():
    return {"Authorization": f"Bearer {mock_jwt_token('test1', 1)}"}


def test_create_task_preserves_text(client: TestClient):
    response = client.post('/tasks/', headers=headers(),
                           json={'text': 'Prepare CI report', 'category_id': 1})
    assert response.status_code == 201
    assert response.json()['text'] == 'Prepare CI report'
    with TestSessionLocal() as db:
        assert db.query(models.Task).one().text == 'Prepare CI report'


def test_create_task_without_category(client: TestClient):
    response = client.post('/tasks/', headers=headers(), json={'text': 'Read docs'})
    assert response.status_code == 201
    assert response.json()['category_id'] is None
    assert response.json()['category_name'] is None


def test_create_completed_task(client: TestClient):
    response = client.post('/tasks/', headers=headers(),
                           json={'text': 'Done task', 'category_id': 1, 'done': True})
    assert response.status_code == 201
    assert response.json()['text'] == 'Done task'
    assert response.json()['done'] is True


def test_create_task_rejects_other_users_category(client: TestClient):
    response = client.post('/tasks/', headers=headers(),
                           json={'text': 'Private task', 'category_id': 2})
    assert response.status_code == 400
    with TestSessionLocal() as db:
        assert db.query(models.Task).count() == 0


def test_create_task_rejects_unknown_category(client: TestClient):
    response = client.post('/tasks/', headers=headers(),
                           json={'text': 'Task', 'category_id': 999})
    assert response.status_code == 400


def test_create_task_requires_authentication(client: TestClient):
    response = client.post('/tasks/', json={'text': 'Task'})
    assert response.status_code == 401
