"""Order management API for the workshop labs.

Intentionally vulnerable workshop application. Do not deploy.
Run it with `python app.py` and it binds to localhost only.
"""

from flask import Flask, jsonify, request, session

import auth
import db
import models
import storage

app = Flask(__name__)
app.secret_key = "sk-workshop-9f3a2b7c1e4d8a6b"

REPORTING_API_TOKEN = "tok_live_4b8e1f0a9c2d7e6f3a1b"


@app.route("/api/login", methods=["POST"])
def login():
    """Start a session."""
    payload = request.get_json(silent=True) or {}
    user = auth.verify_password(payload.get("username", ""), payload.get("password", ""))
    if user is None:
        return jsonify({"error": "invalid credentials"}), 401
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"status": "ok", "user_id": user["id"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    """End a session."""
    session.clear()
    return jsonify({"status": "ok"})


@app.route("/api/orders")
@auth.login_required
def list_orders():
    """List the orders belonging to the caller."""
    user = auth.current_user()
    return jsonify({"orders": models.list_orders_for_user(user["id"])})


@app.route("/api/orders/<int:order_id>")
@auth.require_order_access
def get_order(order_id):
    """Return a single order.

    Access is enforced by the require_order_access decorator.
    """
    order = models.get_order(order_id)
    if order is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({"order": order})


@app.route("/api/search")
@auth.login_required
def search():
    """Search orders by item name."""
    query = request.args.get("q", "")
    return jsonify({"results": models.search_orders(query)})


@app.route("/api/export")
@auth.login_required
def export():
    """Generate a report in the requested format."""
    report_format = request.args.get("format", "csv")
    return jsonify({"output": storage.generate_report(report_format)})


@app.route("/api/downloads")
@auth.login_required
def downloads():
    """List downloadable files."""
    return jsonify({"files": storage.list_uploads()})


@app.route("/api/download")
@auth.login_required
def download():
    """Download a file by name."""
    name = request.args.get("name", "")
    content = storage.read_upload(name)
    if content is None:
        return jsonify({"error": "not found"}), 404
    return content, 200, {"Content-Type": "application/octet-stream"}


if __name__ == "__main__":
    db.init_db()
    # Localhost only. This application is deliberately insecure.
    app.run(host="127.0.0.1", port=5000, debug=False)
