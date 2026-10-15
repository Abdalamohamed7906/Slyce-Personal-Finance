"""Use a throwaway database and no API keys for tests."""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_slyce.db"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-bytes-long"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["TRADING212_API_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_client(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    token = client.post(
        "/auth/login", data={"username": "test@example.com", "password": "password123"}
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
