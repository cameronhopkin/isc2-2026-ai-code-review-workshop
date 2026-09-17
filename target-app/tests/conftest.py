"""Shared fixtures for the target-app tests."""

import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import app as app_module  # noqa: E402
import db  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client backed by a throwaway database."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


def login(test_client, username="alice", password="password123"):
    """Log in and return the response."""
    return test_client.post(
        "/api/login", json={"username": username, "password": password}
    )
