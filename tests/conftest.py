import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "local-test-key-not-for-production")

from fastapi.testclient import TestClient
import pytest

from todo.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as _client:
        yield _client
