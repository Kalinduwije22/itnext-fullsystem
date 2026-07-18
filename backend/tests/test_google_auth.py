from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.modules.auth import service

client = TestClient(app)


class _FakeUser:
    def __init__(self, id_, email):
        self.id = id_
        self.email = email


class _FakeDB:
    def __init__(self, existing_user=None):
        self._existing = existing_user
        self._pending = None

    async def scalar(self, _stmt):
        return self._existing

    def add(self, obj):
        self._pending = obj

    async def flush(self):
        if self._pending is not None and getattr(self._pending, "id", None) is None:
            self._pending.id = "new-user-id"


def _override_for(db):
    async def _gen():
        yield db

    return _gen


def teardown_function(_fn):
    app.dependency_overrides.clear()
    settings.google_client_id = ""


def test_auth_config_reflects_setting():
    settings.google_client_id = "abc123.apps.googleusercontent.com"
    resp = client.get("/api/v1/auth/config")
    assert resp.status_code == 200
    assert resp.json()["google_client_id"] == "abc123.apps.googleusercontent.com"


def test_google_login_503_when_unconfigured():
    settings.google_client_id = ""
    resp = client.post("/api/v1/auth/google", json={"credential": "whatever"})
    assert resp.status_code == 503


def test_google_login_rejects_aud_mismatch(monkeypatch):
    settings.google_client_id = "expected-client-id"
    monkeypatch.setattr(
        service,
        "_fetch_google_tokeninfo",
        AsyncMock(
            return_value={
                "aud": "other-client-id",
                "email_verified": "true",
                "email": "x@example.com",
            }
        ),
    )
    app.dependency_overrides[get_db] = _override_for(_FakeDB())
    resp = client.post("/api/v1/auth/google", json={"credential": "token"})
    assert resp.status_code == 401


def test_google_login_creates_new_user(monkeypatch):
    settings.google_client_id = "expected-client-id"
    monkeypatch.setattr(
        service,
        "_fetch_google_tokeninfo",
        AsyncMock(
            return_value={
                "aud": "expected-client-id",
                "email_verified": "true",
                "email": "newuser@example.com",
                "name": "New User",
            }
        ),
    )
    app.dependency_overrides[get_db] = _override_for(_FakeDB(existing_user=None))
    resp = client.post("/api/v1/auth/google", json={"credential": "token"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_google_login_reuses_existing_user(monkeypatch):
    settings.google_client_id = "expected-client-id"
    monkeypatch.setattr(
        service,
        "_fetch_google_tokeninfo",
        AsyncMock(
            return_value={
                "aud": "expected-client-id",
                "email_verified": "true",
                "email": "existing@example.com",
            }
        ),
    )
    existing = _FakeUser("existing-id", "existing@example.com")
    app.dependency_overrides[get_db] = _override_for(_FakeDB(existing_user=existing))
    resp = client.post("/api/v1/auth/google", json={"credential": "token"})
    assert resp.status_code == 200
