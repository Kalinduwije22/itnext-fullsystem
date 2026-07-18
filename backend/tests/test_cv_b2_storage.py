from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.config import settings
from app.modules.cv import service as cv_service


def _clear_b2_settings():
    settings.b2_endpoint = ""
    settings.b2_region = ""
    settings.b2_key_id = ""
    settings.b2_application_key = ""


def _set_fake_b2_settings():
    settings.b2_endpoint = "https://s3.us-west-004.backblazeb2.com"
    settings.b2_region = "us-west-004"
    settings.b2_key_id = "fake-key-id"
    settings.b2_application_key = "fake-application-key"
    settings.b2_bucket_name = "cvs-test"


def teardown_function(_fn):
    _clear_b2_settings()
    settings.b2_bucket_name = "cvs"


def _fake_create_record(monkeypatch):
    async def _create(db, user_id, blob_url, filename, backend):
        return SimpleNamespace(
            id="doc-1", user_id=user_id, blob_url=blob_url, filename=filename,
            storage_backend=backend,
        )

    monkeypatch.setattr(cv_service, "create_record", _create)


@pytest.mark.asyncio
async def test_falls_back_to_local_when_b2_unconfigured(tmp_path, monkeypatch):
    _clear_b2_settings()
    monkeypatch.setattr(cv_service, "STORAGE_DIR", tmp_path)
    _fake_create_record(monkeypatch)

    doc = await cv_service.upload_and_record(None, "user-1", "resume.pdf", b"%PDF fake")

    assert cv_service.current_backend() == "local"
    assert doc.storage_backend == "local"
    assert (tmp_path / doc.blob_url).read_bytes() == b"%PDF fake"


@pytest.mark.asyncio
async def test_uploads_to_b2_when_configured(monkeypatch):
    _set_fake_b2_settings()
    fake_client = MagicMock()
    monkeypatch.setattr(cv_service, "_b2_client", lambda: fake_client)
    _fake_create_record(monkeypatch)

    doc = await cv_service.upload_and_record(None, "user-1", "resume.pdf", b"%PDF fake")

    assert doc.storage_backend == "b2"
    fake_client.put_object.assert_called_once()
    _, kwargs = fake_client.put_object.call_args
    assert kwargs["Bucket"] == "cvs-test"
    assert kwargs["Key"] == doc.blob_url
    assert kwargs["Body"] == b"%PDF fake"


@pytest.mark.asyncio
async def test_rejects_disallowed_extension_regardless_of_backend():
    _set_fake_b2_settings()
    with pytest.raises(Exception) as exc_info:
        await cv_service.upload_and_record(None, "user-1", "resume.exe", b"data")
    assert getattr(exc_info.value, "status_code", None) == 400


@pytest.mark.asyncio
async def test_rejects_oversized_upload_to_b2(monkeypatch):
    _set_fake_b2_settings()
    fake_client = MagicMock()
    monkeypatch.setattr(cv_service, "_b2_client", lambda: fake_client)

    with pytest.raises(Exception) as exc_info:
        await cv_service.upload_and_record(
            None, "user-1", "resume.pdf", b"x" * (cv_service.MAX_UPLOAD_BYTES + 1)
        )
    assert getattr(exc_info.value, "status_code", None) == 413
    fake_client.put_object.assert_not_called()


def test_tolerates_bare_hostname_endpoint():
    _set_fake_b2_settings()
    settings.b2_endpoint = "s3.us-west-004.backblazeb2.com"  # no scheme
    client = cv_service._b2_client()
    assert client.meta.endpoint_url == "https://s3.us-west-004.backblazeb2.com"


@pytest.mark.asyncio
async def test_fetch_b2_object_reads_body_and_content_type(monkeypatch):
    # fetch_b2_object proxies bytes through our own backend rather than
    # redirecting the browser to B2 directly (see the docstring in
    # cv/service.py for why a redirect breaks CORS). Mock the boto3 client
    # since this is a pure server-side read, not something to hit real B2 for.
    _set_fake_b2_settings()
    fake_body = MagicMock()
    fake_body.read.return_value = b"%PDF fake bytes"
    fake_client = MagicMock()
    fake_client.get_object.return_value = {"Body": fake_body, "ContentType": "application/pdf"}
    monkeypatch.setattr(cv_service, "_b2_client", lambda: fake_client)

    data, content_type = await cv_service.fetch_b2_object("somekey.pdf")

    assert data == b"%PDF fake bytes"
    assert content_type == "application/pdf"
    fake_client.get_object.assert_called_once_with(Bucket="cvs-test", Key="somekey.pdf")
