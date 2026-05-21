import pytest
from ..models import Hero, Mission


@pytest.fixture
def hero(session):
    h = Hero(name="Thor", power="Thunder", level=10, active=True)
    session.add(h)
    session.commit()
    session.refresh(h)
    return h


@pytest.fixture
def mission(session, hero):
    assert hero.id is not None
    m = Mission(title="Save the world", difficulty=5, completed=False, hero_id=hero.id)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


# --- GET /missions ---

def test_get_missions_empty(client):
    response = client.get("/missions")
    assert response.status_code == 200
    assert response.json() == []


def test_get_missions(client, mission):
    response = client.get("/missions")
    assert response.status_code == 200
    assert len(response.json()) == 1


# --- GET /missions/{id} ---

def test_get_mission(client, mission):
    response = client.get(f"/missions/{mission.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Save the world"


def test_get_mission_not_found(client):
    response = client.get("/missions/999")
    assert response.status_code == 404


# --- POST /missions ---

def test_create_mission(client, hero):
    response = client.post("/missions", json={
        "title": "Save the world",
        "difficulty": 5,
        "completed": False,
        "hero_id": hero.id
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Save the world"


def test_create_mission_invalid_hero(client):
    response = client.post("/missions", json={
        "title": "Save the world",
        "difficulty": 5,
        "completed": False,
        "hero_id": 999
    })
    assert response.status_code == 409


# --- PATCH /missions/{id} ---

def test_update_mission(client, mission):
    response = client.patch(f"/missions/{mission.id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_update_mission_not_found(client):
    response = client.patch("/missions/999", json={"completed": True})
    assert response.status_code == 404


# --- DELETE /missions/{id} ---

def test_delete_mission(client, mission):
    response = client.delete(f"/missions/{mission.id}")
    assert response.status_code == 200


def test_delete_mission_not_found(client):
    response = client.delete("/missions/999")
    assert response.status_code == 404
