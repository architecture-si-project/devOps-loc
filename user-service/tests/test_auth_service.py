import datetime

from user_app.services import auth_service


def test_register_user_returns_none_if_user_exists(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda email: (1, "John", email, "hashed", "user"))

    result = auth_service.register_user("John", "john@example.com", "secret")

    assert result is None


def test_register_user_creates_user_when_email_is_new(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda email: None)
    monkeypatch.setattr(auth_service, "hash_password", lambda password: "hashed-password")

    def fake_create_user(name, email, password_hash):
        assert password_hash == "hashed-password"
        return {"id": 1, "name": name, "email": email}

    monkeypatch.setattr(auth_service, "create_user", fake_create_user)

    result = auth_service.register_user("John", "john@example.com", "secret")

    assert result == {"id": 1, "name": "John", "email": "john@example.com"}


def test_authenticate_user_returns_none_for_invalid_password(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda email: (1, "John", email, "hashed", "user"))
    monkeypatch.setattr(auth_service, "check_password", lambda password, hashed: False)

    result = auth_service.authenticate_user("john@example.com", "wrong")

    assert result is None


def test_authenticate_user_returns_token_for_valid_credentials(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda email: (1, "John", email, "hashed", "user"))
    monkeypatch.setattr(auth_service, "check_password", lambda password, hashed: True)
    monkeypatch.setattr(auth_service, "SECRET_KEY", "test-secret")

    def fake_encode(payload, secret_key, algorithm):
        assert payload["user_id"] == 1
        assert payload["role"] == "user"
        assert isinstance(payload["exp"], datetime.datetime)
        assert secret_key == "test-secret"
        assert algorithm == "HS256"
        return "fake-jwt-token"

    monkeypatch.setattr(auth_service.jwt, "encode", fake_encode)

    result = auth_service.authenticate_user("john@example.com", "secret")

    assert result == "fake-jwt-token"


def test_authenticate_user_returns_none_when_user_not_found(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda email: None)

    result = auth_service.authenticate_user("unknown@example.com", "secret")

    assert result is None


def test_hash_password_returns_string():
    result = auth_service.hash_password("mypassword")

    assert isinstance(result, str)
    assert result != "mypassword"


def test_check_password_valid():
    hashed = auth_service.hash_password("mypassword")

    assert auth_service.check_password("mypassword", hashed) is True


def test_check_password_invalid():
    hashed = auth_service.hash_password("mypassword")

    assert auth_service.check_password("wrongpassword", hashed) is False


class FakeCursor:
    def __init__(self, result=None):
        self._result = result

    def execute(self, *args):
        pass

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


def test_get_user_by_email_found(monkeypatch):
    row = (1, "John", "john@test.com", "hashed", "user")
    monkeypatch.setattr(auth_service, "get_connection", lambda: FakeConnection(FakeCursor(row)))

    result = auth_service.get_user_by_email("john@test.com")

    assert result == row


def test_get_user_by_email_not_found(monkeypatch):
    monkeypatch.setattr(auth_service, "get_connection", lambda: FakeConnection(FakeCursor(None)))

    result = auth_service.get_user_by_email("unknown@test.com")

    assert result is None


def test_create_user(monkeypatch):
    monkeypatch.setattr(auth_service, "get_connection", lambda: FakeConnection(FakeCursor((1, "John", "john@test.com"))))

    result = auth_service.create_user("John", "john@test.com", "hashed")

    assert result == {"id": 1, "name": "John", "email": "john@test.com"}



