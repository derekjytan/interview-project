"""Integration tests use a unique schema inside an explicitly supplied Postgres DB."""

import os
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


@pytest.fixture
def database():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        raise pytest.UsageError(
            "Set TEST_DATABASE_URL to a disposable Postgres database."
        )
    url = make_url(url).set(drivername="postgresql+psycopg")
    schema = f"test_{uuid4().hex}"
    admin = create_engine(url)
    with admin.begin() as connection:
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        init_dir = Path(__file__).resolve().parents[2] / "db" / "init"
        with engine.begin() as connection:
            for script in sorted(init_dir.glob("*.sql")):
                # These are literal SQL scripts, including '%' in seed text.
                # Do not pass an empty parameter dict to Psycopg's formatter.
                connection.exec_driver_sql(
                    script.read_text(), execution_options={"no_parameters": True}
                )
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        admin.dispose()


@pytest.fixture
def client(database, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", os.environ["TEST_DATABASE_URL"])
    import db
    from app import app

    sessions = []

    def test_session():
        session = Session(database, expire_on_commit=False)
        sessions.append(session)
        return session

    monkeypatch.setattr(db, "SessionLocal", test_session)
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            test_client.db_sessions = sessions
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def alice(client):
    response = client.post(
        "/api/auth/login", json={"name": "alice", "password": "alice-password"}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}
