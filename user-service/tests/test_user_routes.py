import datetime

import jwt
import pytest

from user_app import create_app

SECRET = "test-secret"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", SECRET)
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def make_token(user_id=1, role="user"):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def auth_header(user_id=1, role="user"):
    return {"Authorization": f"Bearer {make_token(user_id, role)}"}


def test_list_users_returns_401_without_token(client):
    response = client.get("/users")
    assert response.status_code == 401


def test_list_users_returns_200_with_token(client, monkeypatch):
    monkeypatch.setattr("user_app.routes.users.get_all_users", lambda: [])

    response = client.get("/users", headers=auth_header())
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_user_returns_401_without_token(client):
    response = client.get("/users/1")
    assert response.status_code == 401


def test_get_user_returns_404_when_not_found(client, monkeypatch):
    monkeypatch.setattr("user_app.routes.users.get_user_by_id", lambda uid: None)

    response = client.get("/users/1", headers=auth_header())
    assert response.status_code == 404


def test_put_user_returns_403_when_not_owner_nor_admin(client, monkeypatch):
    response = client.put(
        "/users/2",
        json={"name": "New", "email": "new@example.com"},
        headers=auth_header(user_id=1, role="user"),
    )
    assert response.status_code == 403


def test_put_user_allowed_for_owner(client, monkeypatch):
    monkeypatch.setattr(
        "user_app.routes.users.update_user",
        lambda uid, name, email: {"id": uid, "name": name, "email": email},
    )

    response = client.put(
        "/users/1",
        json={"name": "Updated", "email": "updated@example.com"},
        headers=auth_header(user_id=1, role="user"),
    )
    assert response.status_code == 200


def test_put_user_allowed_for_admin(client, monkeypatch):
    monkeypatch.setattr(
        "user_app.routes.users.update_user",
        lambda uid, name, email: {"id": uid, "name": name, "email": email},
    )

    response = client.put(
        "/users/2",
        json={"name": "Updated", "email": "updated@example.com"},
        headers=auth_header(user_id=1, role="admin"),
    )
    assert response.status_code == 200


def test_delete_user_returns_403_for_non_admin(client):
    response = client.delete("/users/1", headers=auth_header(role="user"))
    assert response.status_code == 403


def test_delete_user_allowed_for_admin(client, monkeypatch):
    monkeypatch.setattr("user_app.routes.users.delete_user", lambda uid: True)

    response = client.delete("/users/1", headers=auth_header(role="admin"))
    assert response.status_code == 200


def test_change_role_returns_403_for_non_admin(client):
    response = client.patch("/users/1/role", json={"role": "admin"}, headers=auth_header(role="user"))
    assert response.status_code == 403


def test_change_role_returns_400_for_invalid_role(client):
    response = client.patch("/users/1/role", json={"role": "superuser"}, headers=auth_header(role="admin"))
    assert response.status_code == 400


def test_change_role_allowed_for_admin(client, monkeypatch):
    monkeypatch.setattr(
        "user_app.routes.users.update_user_role",
        lambda uid, role: {"id": uid, "name": "John", "email": "john@example.com", "role": role},
    )

    response = client.patch("/users/1/role", json={"role": "admin"}, headers=auth_header(role="admin"))
    assert response.status_code == 200
    assert response.get_json()["role"] == "admin"
