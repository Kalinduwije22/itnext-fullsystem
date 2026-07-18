from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.admin.schemas import AdminStatsOut
from app.modules.auth.models import User
from app.shared.deps import get_current_user

client = TestClient(app)


def _user(is_admin: bool) -> User:
    return User(
        id="user-1",
        email="user@example.com",
        full_name="Test User",
        hashed_password="x",
        is_active=True,
        is_admin=is_admin,
    )


async def _fake_get_db():
    yield None


def teardown_function(_fn):
    app.dependency_overrides.clear()


def test_stats_forbidden_for_non_admin():
    app.dependency_overrides[get_current_user] = lambda: _user(False)
    app.dependency_overrides[get_db] = _fake_get_db
    resp = client.get("/api/v1/admin/stats")
    assert resp.status_code == 403


def test_stats_ok_for_admin(monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: _user(True)
    app.dependency_overrides[get_db] = _fake_get_db
    canned = AdminStatsOut(
        total_users=3, total_orders=2, paid_orders=1, total_cvs=1, revenue_lkr=4900.0
    )
    monkeypatch.setattr(
        "app.modules.admin.service.get_stats", AsyncMock(return_value=canned)
    )
    resp = client.get("/api/v1/admin/stats")
    assert resp.status_code == 200
    assert resp.json()["total_users"] == 3
