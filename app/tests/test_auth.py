import pytest
from ..models import User
from ..security import hash_password


@pytest.fixture
def registered_user(session):
    user = User(
        username="testuser",
        hashed_password=hash_password("password123"),
        is_admin=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# --- POST /auth/register ---

def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_register_with_existing_username(client, registered_user):
    response = client.post("/auth/register", json={
        "username":registered_user.username,
        "password": "anypassword",
        "is_admin": 0
    })

    assert response.status_code == 400



# --- POST /auth/login ---

def test_login(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/auth/login", data={
        "username": "nobody",
        "password": "password123"
    })
    assert response.status_code == 401


# --- GET /auth/me ---

def test_me(client):
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert "username" in response.json()
    assert "admin" in response.json()
