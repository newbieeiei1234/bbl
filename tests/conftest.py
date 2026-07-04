import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def _test_db_url():
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_booking_")
    os.close(fd)
    yield f"sqlite:///{path}"
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture()
def client(_test_db_url):
    import main
    from db.db_connection import get_db
    from db.models.base import Base

    engine = create_engine(
        _test_db_url, connect_args={"check_same_thread": False}
    )
    TestingSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


def register_user(client, username, password, admin=False):
    return client.post(
        "/register",
        json={"username": username, "password": password, "admin_status": admin},
    )


def login(client, username, password):
    return client.post(
        "/login", json={"username": username, "password": password}
    )


def auth_token(response):
    body = response.json()
    return body.get("access_token")


def auth_header(client, username, password):
    token = auth_token(login(client, username, password))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_user(client):
    username, password = "admin", "adminpass"
    register_user(client, username, password, admin=True)
    return username, password


@pytest.fixture()
def normal_user(client):
    username, password = "alice", "alicepass"
    register_user(client, username, password, admin=False)
    return username, password


@pytest.fixture()
def other_user(client):
    username, password = "bob", "bobpass"
    register_user(client, username, password, admin=False)
    return username, password
