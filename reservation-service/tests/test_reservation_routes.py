import datetime

import jwt
import pytest

from reservation_app import create_app

SECRET = "k7Xp9Qm2wL5nR8vT0jB3cF6hA4sD1eGx"


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
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def auth_header(user_id=1, role="user"):
    return {"Authorization": f"Bearer {make_token(user_id, role)}"}


def test_create_reservation_returns_401_without_token(client):
    response = client.post("/reservations", json={
        "housing_name": "Apt Paris",
        "check_in": "2026-07-01",
        "check_out": "2026-07-05",
    })
    assert response.status_code == 401


def test_create_reservation_returns_400_when_fields_missing(client):
    response = client.post("/reservations", json={"housing_name": "Apt Paris"}, headers=auth_header())
    assert response.status_code == 400


def test_create_reservation_returns_201(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.create_reservation",
        lambda uid, name, ci, co: {
            "id": 1, "user_id": uid, "housing_name": name,
            "check_in": ci, "check_out": co, "status": "confirmed",
        },
    )

    response = client.post("/reservations", json={
        "housing_name": "Apt Paris",
        "check_in": "2026-07-01",
        "check_out": "2026-07-05",
    }, headers=auth_header())

    assert response.status_code == 201
    assert response.get_json()["housing_name"] == "Apt Paris"


def test_list_reservations_returns_200(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservations_by_user",
        lambda uid: [],
    )

    response = client.get("/reservations", headers=auth_header())
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_reservation_returns_404(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: None,
    )

    response = client.get("/reservations/1", headers=auth_header())
    assert response.status_code == 404


def test_get_reservation_returns_403_for_other_user(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: {
            "id": 1, "user_id": 99, "housing_name": "Apt",
            "check_in": "2026-07-01", "check_out": "2026-07-05", "status": "confirmed",
        },
    )

    response = client.get("/reservations/1", headers=auth_header(user_id=1))
    assert response.status_code == 403


def test_get_reservation_returns_200_for_owner(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: {
            "id": 1, "user_id": 1, "housing_name": "Apt",
            "check_in": "2026-07-01", "check_out": "2026-07-05", "status": "confirmed",
        },
    )

    response = client.get("/reservations/1", headers=auth_header(user_id=1))
    assert response.status_code == 200


def test_get_reservation_returns_200_for_admin(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: {
            "id": 1, "user_id": 99, "housing_name": "Apt",
            "check_in": "2026-07-01", "check_out": "2026-07-05", "status": "confirmed",
        },
    )

    response = client.get("/reservations/1", headers=auth_header(user_id=1, role="admin"))
    assert response.status_code == 200


def test_cancel_returns_404(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: None,
    )

    response = client.delete("/reservations/1", headers=auth_header())
    assert response.status_code == 404


def test_cancel_returns_403_for_other_user(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: {
            "id": 1, "user_id": 99, "housing_name": "Apt",
            "check_in": "2026-07-01", "check_out": "2026-07-05", "status": "confirmed",
        },
    )

    response = client.delete("/reservations/1", headers=auth_header(user_id=1))
    assert response.status_code == 403


def test_cancel_returns_200(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: {
            "id": 1, "user_id": 1, "housing_name": "Apt",
            "check_in": "2026-07-01", "check_out": "2026-07-05", "status": "confirmed",
        },
    )
    monkeypatch.setattr(
        "reservation_app.routes.reservations.cancel_reservation",
        lambda rid: True,
    )

    response = client.delete("/reservations/1", headers=auth_header(user_id=1))
    assert response.status_code == 200


def test_cancel_already_cancelled(client, monkeypatch):
    monkeypatch.setattr(
        "reservation_app.routes.reservations.get_reservation_by_id",
        lambda rid: {
            "id": 1, "user_id": 1, "housing_name": "Apt",
            "check_in": "2026-07-01", "check_out": "2026-07-05", "status": "cancelled",
        },
    )
    monkeypatch.setattr(
        "reservation_app.routes.reservations.cancel_reservation",
        lambda rid: False,
    )

    response = client.delete("/reservations/1", headers=auth_header(user_id=1))
    assert response.status_code == 400
