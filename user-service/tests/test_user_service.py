from user_app.services import user_service


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


def test_get_all_users(monkeypatch):
    rows = [(1, "John", "john@test.com"), (2, "Jane", "jane@test.com")]
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor(rows)))

    result = user_service.get_all_users()

    assert len(result) == 2
    assert result[0] == {"id": 1, "name": "John", "email": "john@test.com"}


def test_get_user_by_id_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor((1, "John", "john@test.com"))))

    result = user_service.get_user_by_id(1)

    assert result == {"id": 1, "name": "John", "email": "john@test.com"}


def test_get_user_by_id_not_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor(None)))

    result = user_service.get_user_by_id(999)

    assert result is None


def test_update_user_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor((1, "Updated", "new@test.com"))))

    result = user_service.update_user(1, "Updated", "new@test.com")

    assert result == {"id": 1, "name": "Updated", "email": "new@test.com"}


def test_update_user_not_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor(None)))

    result = user_service.update_user(999, "Name", "email@test.com")

    assert result is None


def test_delete_user_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor((1,))))

    result = user_service.delete_user(1)

    assert result is True


def test_delete_user_not_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor(None)))

    result = user_service.delete_user(999)

    assert result is False


def test_update_user_role_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor((1, "John", "john@test.com", "admin"))))

    result = user_service.update_user_role(1, "admin")

    assert result == {"id": 1, "name": "John", "email": "john@test.com", "role": "admin"}


def test_update_user_role_not_found(monkeypatch):
    monkeypatch.setattr(user_service, "get_connection", lambda: FakeConnection(FakeCursor(None)))

    result = user_service.update_user_role(999, "admin")

    assert result is None
