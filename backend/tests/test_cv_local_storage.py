import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.models import User
from app.modules.cv import service as cv_service
from app.shared.deps import get_current_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(cv_service, "STORAGE_DIR", tmp_path)
    yield tmp_path


def test_save_local_file_rejects_bad_key(tmp_path):
    with pytest.raises(Exception):
        cv_service.save_local_file("../../etc/passwd", b"data")
    assert list(tmp_path.iterdir()) == []


def test_save_local_file_rejects_oversized_payload():
    key = "0" * 32 + ".pdf"
    with pytest.raises(Exception):
        cv_service.save_local_file(key, b"x" * (cv_service.MAX_UPLOAD_BYTES + 1))


def test_save_and_read_local_file(tmp_path):
    key = "1" * 32 + ".pdf"
    cv_service.save_local_file(key, b"%PDF-1.4 fake content")
    path = cv_service.local_file_path(key)
    assert path.exists()
    assert path.read_bytes() == b"%PDF-1.4 fake content"


def _admin_user():
    return User(
        id="admin-1",
        email="admin@example.com",
        full_name="Admin",
        hashed_password="x",
        is_active=True,
        is_admin=True,
    )


class _FakeDB:
    async def get(self, _model, _id):
        return None


async def _fake_get_db():
    yield _FakeDB()


def test_admin_download_404_when_cv_missing():
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[get_db] = _fake_get_db
    try:
        resp = client.get("/api/v1/admin/cvs/does-not-exist/download")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
