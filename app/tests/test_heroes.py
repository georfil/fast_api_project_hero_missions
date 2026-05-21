import pytest
from ..models import Hero, Mission

# =========================================
# Initialise Heroes for Testing
# =========================================

@pytest.fixture
def hero(session):
    h = Hero(name="Thor", power="Thunder", level=10, active=True)
    session.add(h)
    session.commit()
    session.refresh(h)
    return h


@pytest.fixture
def hero_with_active_mission(session):
    h = Hero(name="Thor", power="Thunder", level=10, active=True)
    session.add(h)
    session.commit()
    session.refresh(h)
    assert h.id is not None
    m = Mission(title="Save the world", difficulty=5, completed=False, hero_id=h.id)
    session.add(m)
    session.commit()
    return h


# --- GET /heroes ---

def test_get_heroes_empty(client):
    response = client.get("/heroes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_heroes(client, hero):
    response = client.get("/heroes")
    assert response.status_code == 200
    assert len(response.json()) == 1


# --- GET /heroes/{id} ---

def test_get_hero(client, hero):
    response = client.get(f"/heroes/{hero.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Thor"


def test_get_hero_not_found(client):
    response = client.get("/heroes/999")
    assert response.status_code == 404


# --- POST /heroes ---

def test_create_hero(client):
    response = client.post("/heroes", json={
        "name": "Thor",
        "power": "Thunder",
        "level": 10,
        "active": True
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Thor"


# --- PATCH /heroes/{id} ---

def test_update_hero(client, hero):
    response = client.patch(f"/heroes/{hero.id}", json={"level": 99})
    assert response.status_code == 200
    assert response.json()["level"] == 99


def test_update_hero_not_found(client):
    response = client.patch("/heroes/999", json={"level": 99})
    assert response.status_code == 404


# --- DELETE /heroes/{id} ---

def test_delete_hero(client, hero):
    response = client.delete(f"/heroes/{hero.id}")
    assert response.status_code == 200


def test_delete_hero_not_found(client):
    response = client.delete("/heroes/999")
    assert response.status_code == 404


def test_delete_hero_with_active_mission(client, hero_with_active_mission):
    response = client.delete(f"/heroes/{hero_with_active_mission.id}")
    assert response.status_code == 409
