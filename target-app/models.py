"""Data access for users and orders.

Intentionally vulnerable workshop application. Do not deploy.
"""

from db import get_conn


def get_user_by_username(username):
    """Look up a user by name. Parameterized, so this one is fine."""
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, username, password_hash, email FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_order(order_id):
    """Fetch a single order by id.

    Returns the order regardless of who owns it. The caller is responsible
    for deciding whether the requester is allowed to see it.
    """
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, user_id, item, total_cents FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_orders_for_user(user_id):
    """Fetch every order belonging to one user."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, user_id, item, total_cents FROM orders WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_orders(query):
    """Search orders by item name.

    Wraps the caller's term in wildcards so a partial name matches.
    """
    conn = get_conn()
    try:
        sql = "SELECT id, item FROM orders WHERE item LIKE '%%%s%%'" % query
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
