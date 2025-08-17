import importlib
import sqlite3
import sys
from pathlib import Path

import pytest


class CursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        sql = sql.replace("%s", "?")
        if params is None:
            return self._cursor.execute(sql)
        return self._cursor.execute(sql, params)

    def __getattr__(self, item):
        return getattr(self._cursor, item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._cursor.close()


class SQLiteConnection(sqlite3.Connection):
    def cursor(self, *args, **kwargs):
        cur = super().cursor(*args, **kwargs)
        return CursorWrapper(cur)


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Create a Flask test client using a temporary SQLite database."""
    db_path = tmp_path / "test.db"

    class SQLitePool:
        def getconn(self):
            return sqlite3.connect(db_path, factory=SQLiteConnection)

        def putconn(self, conn):
            conn.close()

    def fake_init_connection_pool():
        return SQLitePool()

    def fake_migrate_db(db):
        conn = db.getconn()
        with conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS transactions (date TEXT, amount REAL, account TEXT);"
            )
        db.putconn(conn)

    # Ensure project root is on sys.path
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    # Provide required environment variables so connect_tcp imports cleanly
    monkeypatch.setenv("DATABASE_HOST", "localhost")
    monkeypatch.setenv("DATABASE_NAME", "db")
    monkeypatch.setenv("DATABASE_USER", "user")
    monkeypatch.setenv("DATABASE_PASSWORD", "password")

    import connect_tcp
    import migrate

    monkeypatch.setattr(connect_tcp, "init_connection_pool", fake_init_connection_pool)
    monkeypatch.setattr(migrate, "migrate_db", fake_migrate_db)

    # Ensure a fresh import of the app module for each test
    sys.modules.pop("app", None)
    app_module = importlib.import_module("app")

    with app_module.app.test_client() as client:
        yield client


def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_post_and_get_transactions(client):
    data = {"date": "2023-01-01", "amount": "10.5", "account": "Checking"}
    post_resp = client.post("/", data=data)
    assert post_resp.status_code == 200

    resp = client.get("/transactions")
    assert resp.status_code == 200
    body = resp.data
    assert b"Checking" in body
    assert b"10.5" in body
    assert b"2023-01-01" in body
