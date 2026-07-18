from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.models import User
from app.modules.cv import service as cv_service
from app.shared.deps import get_current_user

client = TestClient(app)


def _fake_user() -> User:
    return User(
        id="user-1",
        email="user@example.com",
        full_name="Test User",
        hashed_password="x",
        is_active=True,
        is_admin=False,
    )


async def _fake_get_db():
    yield None


def setup_module(_module):
    app.dependency_overrides[get_current_user] = _fake_user
    app.dependency_overrides[get_db] = _fake_get_db


def teardown_module(_module):
    app.dependency_overrides.clear()


def test_upload_blocked_when_unpaid(monkeypatch):
    monkeypatch.setattr(
        "app.modules.payments.service.has_paid_order", AsyncMock(return_value=False)
    )
    resp = client.post(
        "/api/v1/cv/upload", files={"file": ("cv.pdf", b"%PDF fake", "application/pdf")}
    )
    assert resp.status_code == 402


def test_upload_allowed_when_paid(monkeypatch):
    monkeypatch.setattr(
        "app.modules.payments.service.has_paid_order", AsyncMock(return_value=True)
    )
    fake_doc = SimpleNamespace(
        id="doc-1",
        filename="cv.pdf",
        status="uploaded",
        parsed=None,
        is_current=True,
        created_at=datetime.utcnow(),
        grade_score=None,
        grade_feedback=None,
        graded_at=None,
        grade_acknowledged=False,
    )
    monkeypatch.setattr(cv_service, "upload_and_record", AsyncMock(return_value=fake_doc))
    monkeypatch.setattr(cv_service, "parse_cv", AsyncMock())

    resp = client.post(
        "/api/v1/cv/upload", files={"file": ("cv.pdf", b"%PDF fake", "application/pdf")}
    )
    assert resp.status_code == 200
    assert resp.json()["filename"] == "cv.pdf"


def test_upload_rejects_disallowed_extension(monkeypatch):
    monkeypatch.setattr(
        "app.modules.payments.service.has_paid_order", AsyncMock(return_value=True)
    )
    resp = client.post(
        "/api/v1/cv/upload", files={"file": ("cv.exe", b"data", "application/octet-stream")}
    )
    assert resp.status_code == 400
