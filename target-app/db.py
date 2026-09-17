"""Database connection and first-run seeding.

Intentionally vulnerable workshop application. Do not deploy.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    item TEXT NOT NULL,
    total_cents INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
"""

# Two users, each owning a few orders. Order ids are sequential across
# users on purpose, so walking /api/orders/<id> crosses the boundary.
SEED_USERS = [
    (1, "alice", "pbkdf2$demo$alice-not-a-real-hash", "alice@example.com"),
    (2, "bob", "pbkdf2$demo$bob-not-a-real-hash", "bob@example.com"),
]

SEED_ORDERS = [
    (1, 1, "Mechanical keyboard", 12900),
    (2, 1, "USB-C hub", 4500),
    (3, 1, "Monitor arm", 8900),
    (4, 2, "Noise cancelling headphones", 24900),
    (5, 2, "Laptop stand", 3900),
]


def get_conn():
    """Open a connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the schema and seed it on first run. Idempotent."""
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        already_seeded = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if not already_seeded:
            conn.executemany(
                "INSERT INTO users (id, username, password_hash, email) VALUES (?, ?, ?, ?)",
                SEED_USERS,
            )
            conn.executemany(
                "INSERT INTO orders (id, user_id, item, total_cents) VALUES (?, ?, ?, ?)",
                SEED_ORDERS,
            )
            conn.commit()
    finally:
        conn.close()


def reset_db():
    """Drop the database file. Used by the test suite."""
    if DB_PATH.exists():
        DB_PATH.unlink()
