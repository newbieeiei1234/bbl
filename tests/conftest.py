"""
Shared pytest fixtures for the appointment-booking backend tests.

The fixtures spin the FastAPI app up against an **isolated, throwaway SQLite
database** (a fresh file per test session) so the tests never touch the real
`database.db`. The app's `get_db` dependency is overridden to point at that test
database.

NOTE: These tests target the *intended* REST API described in the assessment.
They are written to pass once the backend is complete and correct. As of now the
backend does not import cleanly (missing `db/models/base.py`, `Bool` import in
`users.py`, booking router not wired into `main.py`), so collection/import will
fail until those are fixed. That is by design — the suite documents the target
behaviour and turns green as the backend is finished.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def _test_db_url():
    """A temp SQLite file used only for the test session."""
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_booking_")
    os.close(fd)
    yield f"sqlite:///{path}"
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture()
def client(_test_db_url):
    """
    A TestClient wired to an isolated test database.

    Each test gets a clean schema (all tables dropped + recreated) so tests are
    independent and order-insensitive.
    """
    # Imported here (not at module top) so that an import error in the app
    # surfaces as a test failure rather than a collection crash for the whole run.
    import main
    from db.db_connection import get_db
    from db.models.base import Base

    engine = create_engine(
        _test_db_url, connect_args={"check_same_thread": False}
    )
    TestingSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

    # Fresh schema for every test.
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


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def register_user(client, username, password, admin=False):
    """Register a user via the public API. Returns the response."""
    return client.post(
        "/register",
        json={"username": username, "password": password, "admin_status": admin},
    )


def login(client, username, password):
    """Log a user in and return the raw response."""
    return client.post(
        "/login", json={"username": username, "password": password}
    )


def auth_token(response):
    """
    Pull the bearer token out of a /login response body, tolerating the
    documented field name `access_token`.
    """
    body = response.json()
    return body.get("access_token")


def auth_header(client, username, password):
    """Register-independent helper: log in and build an Authorization header."""
    token = auth_token(login(client, username, password))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_user(client):
    """A pre-registered admin user. Returns (username, password)."""
    username, password = "admin", "adminpass"
    register_user(client, username, password, admin=True)
    return username, password


@pytest.fixture()
def normal_user(client):
    """A pre-registered non-admin user. Returns (username, password)."""
    username, password = "alice", "alicepass"
    register_user(client, username, password, admin=False)
    return username, password


@pytest.fixture()
def other_user(client):
    """A second non-admin user, to test ownership isolation."""
    username, password = "bob", "bobpass"
    register_user(client, username, password, admin=False)
    return username, password
