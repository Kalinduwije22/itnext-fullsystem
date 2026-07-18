from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app

client = TestClient(app)

VALID = {
    "email": "valid@example.com",
    "full_name": "Valid Name",
    "password": "goodpass123",
    "phone": "+94771234567",
}


class _FakeDB:
    """Enough of AsyncSession for register(): no existing user, and flush()
    assigns an id the way a real INSERT would."""

    def __init__(self):
        self._pending = None

    async def scalar(self, _stmt):
        return None

    def add(self, obj):
        self._pending = obj

    async def flush(self):
        """Mimic the column defaults a real flush() would apply."""
        if self._pending is None:
            return
        if getattr(self._pending, "id", None) is None:
            self._pending.id = "test-user-id"
        if getattr(self._pending, "is_admin", None) is None:
            self._pending.is_admin = False
        if getattr(self._pending, "is_active", None) is None:
            self._pending.is_active = True


async def _fake_get_db():
    yield _FakeDB()


def setup_module(_module):
    app.dependency_overrides[get_db] = _fake_get_db


def teardown_module(_module):
    app.dependency_overrides.clear()


def test_rejects_short_password():
    resp = client.post("/api/v1/auth/register", json={**VALID, "password": "short1"})
    assert resp.status_code == 422


def test_rejects_password_without_digit():
    resp = client.post(
        "/api/v1/auth/register", json={**VALID, "password": "alllettersnodigits"}
    )
    assert resp.status_code == 422


def test_rejects_blank_name():
    resp = client.post("/api/v1/auth/register", json={**VALID, "full_name": "   "})
    assert resp.status_code == 422


def test_rejects_malformed_phone():
    resp = client.post("/api/v1/auth/register", json={**VALID, "phone": "0771234567"})
    assert resp.status_code == 422


def test_accepts_valid_payload():
    resp = client.post("/api/v1/auth/register", json=VALID)
    assert resp.status_code == 201
    assert resp.json()["phone"] == VALID["phone"]
