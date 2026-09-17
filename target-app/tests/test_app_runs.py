"""The application works as intended.

These tests prove the app is a functioning order API, so that the exploit
tests in test_planted_bugs.py are demonstrating real defects rather than
a broken application.
"""

from conftest import login


def test_login_succeeds_with_seeded_user(client):
    response = login(client, "alice")
    assert response.status_code == 200
    assert response.get_json()["user_id"] == 1


def test_login_fails_with_bad_password(client):
    response = login(client, "alice", "wrong-password")
    assert response.status_code == 401


def test_orders_require_authentication(client):
    response = client.get("/api/orders")
    assert response.status_code == 401


def test_alice_sees_only_her_own_orders_on_the_list_route(client):
    login(client, "alice")
    orders = client.get("/api/orders").get_json()["orders"]
    assert len(orders) == 3
    assert {o["user_id"] for o in orders} == {1}


def test_bob_sees_only_his_own_orders_on_the_list_route(client):
    login(client, "bob")
    orders = client.get("/api/orders").get_json()["orders"]
    assert len(orders) == 2
    assert {o["user_id"] for o in orders} == {2}


def test_search_returns_matching_orders(client):
    login(client, "alice")
    results = client.get("/api/search?q=keyboard").get_json()["results"]
    assert [r["item"] for r in results] == ["Mechanical keyboard"]


def test_downloads_lists_the_upload_directory(client):
    login(client, "alice")
    files = client.get("/api/downloads").get_json()["files"]
    assert "invoice-1001.txt" in files


def test_download_returns_an_upload(client):
    login(client, "alice")
    response = client.get("/api/download?name=invoice-1001.txt")
    assert response.status_code == 200
    assert b"Invoice 1001" in response.data
