import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool

from ..db import get_session
from ..dependencies import get_current_user, get_current_admin
from ..main import app
from ..models import User

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

mock_user = User(id=1, username="testuser", hashed_password="hashed", is_admin=False)
mock_admin = User(id=1, username="adminuser", hashed_password="hashed", is_admin=True)


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = lambda: mock_user
app.dependency_overrides[get_current_admin] = lambda: mock_admin


@pytest.fixture(autouse=True)
def reset_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    with Session(engine) as s:
        yield s
