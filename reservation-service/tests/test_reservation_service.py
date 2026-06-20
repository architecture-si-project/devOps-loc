from reservation_app.services import reservation_service


class FakeCursor:
    def __init__(self, result=None):
        self._result = result

    def execute(self, *args):
        pass

    def fetchall(self):
        return self._result or []

    def fetchone(self):
        return self._result

    def close(self):
        pass


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def close(self):
        pass


def test_create_reservation(monkeypatch):
    row = (1, 1, "Apt Paris", "2026-07-01", "2026-07-05", "confirmed")
    monkeypatch.setattr(reservation_service, "get_connection", lambda: FakeConnection(FakeCursor(row)))

    result = reservation_service.create_reservation(1, "Apt Paris", "2026-07-01", "2026-07-05")

    assert result["id"] == 1
    assert result["status"] == "confirmed"


def test_get_reservations_by_user(monkeypatch):
    rows = [
        (1, 1, "Apt Paris", "2026-07-01", "2026-07-05", "confirmed"),
        (2, 1, "Apt Lyon", "2026-08-01", "2026-08-03", "confirmed"),
    ]
    monkeypatch.setattr(reservation_service, "get_connection", lambda: FakeConnection(FakeCursor(rows)))

    result = reservation_service.get_reservations_by_user(1)

    assert len(result) == 2
    assert result[0]["housing_name"] == "Apt Paris"


def test_get_reservation_by_id_found(monkeypatch):
    row = (1, 1, "Apt Paris", "2026-07-01", "2026-07-05", "confirmed")
    monkeypatch.setattr(reservation_service, "get_connection", lambda: FakeConnection(FakeCursor(row)))

    result = reservation_service.get_reservation_by_id(1)

    assert result["id"] == 1


def test_get_reservation_by_id_not_found(monkeypatch):
    monkeypatch.setattr(reservation_service, "get_connection", lambda: FakeConnection(FakeCursor(None)))

    result = reservation_service.get_reservation_by_id(999)

    assert result is None


def test_cancel_reservation_success(monkeypatch):
    monkeypatch.setattr(reservation_service, "get_connection", lambda: FakeConnection(FakeCursor((1,))))

    result = reservation_service.cancel_reservation(1)

    assert result is True


def test_cancel_reservation_not_found(monkeypatch):
    monkeypatch.setattr(reservation_service, "get_connection", lambda: FakeConnection(FakeCursor(None)))

    result = reservation_service.cancel_reservation(999)

    assert result is False
