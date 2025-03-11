import pytest
from fastapi.testclient import TestClient

from user_service.main import app
from user_service.database import Base, engine


engine_test = engine

client = TestClient(app, base_url="http://testserver")

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

def test_register_user():
    payload = {
        "login": "testuser",
        "email": "test@example.com",
        "password": "secret123"
    }
    response = client.post("/users/register", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["login"] == payload["login"]
    assert data["email"] == payload["email"]

def test_register_duplicate_user():
    payload = {
        "login": "testuser",
        "email": "test@example.com",
        "password": "secret123"
    }
    response = client.post("/users/register", json=payload)
    assert response.status_code == 200, response.text
    response = client.post("/users/register", json=payload)
    assert response.status_code == 400
