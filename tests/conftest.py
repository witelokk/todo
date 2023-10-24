import os

from fastapi.testclient import TestClient
import pytest

from todo.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as _client:
        yield _client
