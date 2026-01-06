import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import Base, engine

# Create a dedicated session factory for testing
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_and_drop_db():
    """Create and drop the database schema for each test run."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Return a fresh TestClient instance for each test."""
    return TestClient(app)


def test_register_user(client):
    """Ensure a new user can register successfully."""
    response = client.post(
        "/auth/register",
        json={
            "username": "tester",
            "email": "tester@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "tester@example.com"
    assert data["username"] == "tester"


def test_register_duplicate_email(client):
    """Ensure duplicate email registration is rejected."""
    client.post(
        "/auth/register",
        json={
            "username": "tester",
            "email": "tester@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )
    response = client.post(
        "/auth/register",
        json={
            "username": "tester2",
            "email": "tester@example.com",
            "full_name": "Another User",
            "password": "secret456",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"] == "Email already registered"


def test_login_success(client):
    """Ensure a registered user can log in with correct credentials."""
    client.post(
        "/auth/register",
        json={
            "username": "tester",
            "email": "tester@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )
    response = client.post(
        "/auth/login", data={"username": "tester@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    """Ensure login fails with an incorrect password."""
    client.post(
        "/auth/register",
        json={
            "username": "tester",
            "email": "tester@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": "tester@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid credentials"
