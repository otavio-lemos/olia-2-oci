import pytest
from fastapi.testclient import TestClient
from rag.api import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_list_workflows():
    client = TestClient(app)
    response = client.get("/workflows")
    assert response.status_code == 200
