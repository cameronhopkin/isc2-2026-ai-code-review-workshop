"""Session handling and access control decorators.

Intentionally vulnerable workshop application. Do not deploy.
"""

from functools import wraps

from flask import jsonify, session

import models


def current_user():
    """Return the logged in user, or None."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return {"id": user_id, "username": session.get("username")}


def login_required(view):
    """Reject callers who have not logged in."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return jsonify({"error": "authentication required"}), 401
        return view(*args, **kwargs)

    return wrapper


def require_order_access(view):
    """Guard an order route.

    Confirms there is a valid session before the view runs, so order
    routes do not have to repeat the check themselves.
    """

    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "authentication required"}), 401
        return view(*args, **kwargs)

    return wrapper


def verify_password(username, password):
    """Check a login. Demo comparison, not a real password check."""
    user = models.get_user_by_username(username)
    if user is None:
        return None
    if user["password_hash"] == "pbkdf2$demo$%s-not-a-real-hash" % username:
        if password == "password123":
            return user
    return None
