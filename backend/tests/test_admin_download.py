from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.admin import router as admin_router
from app.modules.auth.models import User
from app.shared.deps import get_current_user

client = TestClient(app)


class _FakeDoc:
    def __init__(self, storage_backend, blob_url="abc123.pdf", filename="resume.pdf"):
        self.id = "cv-1"
        self.blob_url = blob_url
        self.filename = filename
        self.storage_backend = storage_backend


class _FakeDB:
    def __init__(self, doc):
        self._doc = doc

    async def get(self, _model, _id):
        return self._doc


def _admin_user():
    return User(
        id="admin-1",
        email="admin@example.com",
        full_name="Admin",
        hashed_password="x",
        is_active=True,
        is_admin=True,
    )


def _override_for(doc):
    async def _gen():
        yield _FakeDB(doc)

    return _gen


def setup_module(_module):
    app.dependency_overrides[get_current_user] = _admin_user


def teardown_module(_module):
    app.dependency_overrides.clear()


def test_b2_backed_cv_streams_bytes_directly_no_redirect(monkeypatch):
    # This is the fix for the CORS bug: the response must be the actual file
    # bytes from our own API, never a redirect to a different origin.
    app.dependency_overrides[get_db] = _override_for(_FakeDoc(storage_backend="b2"))
    monkeypatch.setattr(
        admin_router.cv_service,
        "fetch_b2_object",
        _async_return((b"%PDF fake content", "application/pdf")),
    )
    resp = client.get("/api/v1/admin/cvs/cv-1/download", follow_redirects=False)
    assert resp.status_code == 200
    assert resp.content == b"%PDF fake content"
    assert resp.headers["content-type"] == "application/pdf"
    assert "resume.pdf" in resp.headers["content-disposition"]


def test_b2_backed_cv_404s_when_object_missing(monkeypatch):
    from botocore.exceptions import ClientError

    app.dependency_overrides[get_db] = _override_for(_FakeDoc(storage_backend="b2"))

    async def _raise(_blob_url):
        raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")

    monkeypatch.setattr(admin_router.cv_service, "fetch_b2_object", _raise)
    resp = client.get("/api/v1/admin/cvs/cv-1/download")
    assert resp.status_code == 404


def test_local_backed_cv_serves_file(tmp_path, monkeypatch):
    local_path = tmp_path / "abc123.pdf"
    local_path.write_bytes(b"%PDF local content")
    monkeypatch.setattr(admin_router.cv_service, "local_file_path", lambda blob_url: local_path)
    app.dependency_overrides[get_db] = _override_for(_FakeDoc(storage_backend="local"))
    resp = client.get("/api/v1/admin/cvs/cv-1/download")
    assert resp.status_code == 200
    assert resp.content == b"%PDF local content"


def test_local_backed_cv_404s_when_file_missing(tmp_path, monkeypatch):
    missing = tmp_path / "does-not-exist.pdf"
    monkeypatch.setattr(admin_router.cv_service, "local_file_path", lambda blob_url: missing)
    app.dependency_overrides[get_db] = _override_for(_FakeDoc(storage_backend="local"))
    resp = client.get("/api/v1/admin/cvs/cv-1/download")
    assert resp.status_code == 404


def _async_return(value):
    async def _fn(_blob_url):
        return value

    return _fn
