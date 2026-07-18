"""CV upload + async parsing.

Flow:
  1. client POSTs the file to /cv/upload (multipart) -> upload_and_record()
     stores the bytes server-side (B2 or local disk) and creates the row
     (status=uploaded). Uploads are proxied through this API rather than
     PUT straight from the browser to blob storage, for the same CORS
     reason documented on fetch_b2_object() below.
  2. background task parses   -> parse_cv()       (Gemini API -> structured JSON)
"""
import re
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.modules.cv.models import CVDocument

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
# Storage keys are always uuid4-hex + a known extension, generated only by
# upload_and_record() below — this regex guards save_local_file() against
# writing anywhere outside STORAGE_DIR (only relevant to the local-disk
# fallback; B2 keys aren't touched by it).
_KEY_RE = re.compile(r"^[0-9a-f]{32}\.(pdf|doc|docx)$")

STORAGE_DIR = Path(settings.cv_storage_dir)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _b2_configured() -> bool:
    return bool(settings.b2_endpoint and settings.b2_key_id and settings.b2_application_key)


def _b2_client():
    # B2's dashboard often shows the endpoint as a bare hostname
    # (s3.<region>.backblazeb2.com) rather than a full URL — tolerate either.
    endpoint = settings.b2_endpoint
    if endpoint and not endpoint.startswith("http"):
        endpoint = f"https://{endpoint}"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.b2_key_id,
        aws_secret_access_key=settings.b2_application_key,
        region_name=settings.b2_region or None,
    )


def save_local_file(key: str, data: bytes) -> None:
    if not _KEY_RE.match(key):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid upload key")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large (max 10MB)")
    (STORAGE_DIR / key).write_bytes(data)


def local_file_path(blob_url: str) -> Path:
    return STORAGE_DIR / blob_url


def current_backend() -> str:
    """Which backend a file uploaded right now would land in. Captured onto
    the CVDocument row at upload-time — see upload_and_record()."""
    return "b2" if _b2_configured() else "local"


async def fetch_b2_object(blob_url: str) -> tuple[bytes, str]:
    """Fetch a B2 object's bytes server-side for admin downloads.

    Deliberately NOT a presigned-redirect: when a browser request that's
    already cross-origin (frontend -> this API) gets redirected to a THIRD
    origin (B2), the spec requires the browser replace the redirected
    request's Origin header with an opaque "null" — which never matches a
    real CORS allow-list, so B2 silently omits CORS headers and the browser
    blocks reading the response, even though the HTTP request itself
    succeeds. Proxying the bytes through our own (already-CORS-configured)
    API sidesteps this entirely — the browser never talks to B2 directly
    at all, for downloads or uploads (see upload_and_record() below).
    """
    def _fetch():
        obj = _b2_client().get_object(Bucket=settings.b2_bucket_name, Key=blob_url)
        return obj["Body"].read(), obj.get("ContentType") or "application/octet-stream"

    return await run_in_threadpool(_fetch)


async def upload_and_record(
    db: AsyncSession, user_id: str, filename: str, data: bytes
) -> CVDocument:
    """Validate, store, and record an uploaded CV in one server-side step.

    Never redirects the browser to blob storage directly — see
    fetch_b2_object() below for why that breaks CORS on B2. The whole file
    is small (10MB cap) so proxying it through this API is cheap.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Only .pdf, .doc, .docx files are allowed"
        )
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large (max 10MB)")

    key = f"{uuid.uuid4().hex}{ext}"
    backend = current_backend()
    if backend == "b2":
        await run_in_threadpool(
            _b2_client().put_object, Bucket=settings.b2_bucket_name, Key=key, Body=data
        )
    else:
        save_local_file(key, data)

    return await create_record(db, user_id, key, filename, backend)


async def create_record(
    db: AsyncSession, user_id: str, blob_url: str, filename: str, storage_backend: str
) -> CVDocument:
    # A re-upload supersedes whatever was current before it — the new row
    # starts ungraded, which is how re-grading naturally "resets".
    await db.execute(
        update(CVDocument)
        .where(CVDocument.user_id == user_id, CVDocument.is_current.is_(True))
        .values(is_current=False)
    )
    doc = CVDocument(
        user_id=user_id, blob_url=blob_url, filename=filename, storage_backend=storage_backend
    )
    db.add(doc)
    await db.flush()
    return doc


async def get_current_cv(db: AsyncSession, user_id: str) -> CVDocument | None:
    result = await db.scalars(
        select(CVDocument)
        .where(CVDocument.user_id == user_id, CVDocument.is_current.is_(True))
        .order_by(CVDocument.created_at.desc())
        .limit(1)
    )
    return result.first()


async def acknowledge_grade(db: AsyncSession, cv_id: str, user_id: str) -> CVDocument:
    doc = await db.get(CVDocument, cv_id)
    if not doc or doc.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "CV not found")
    doc.grade_acknowledged = True
    await db.commit()
    await db.refresh(doc)
    return doc


async def build_download_response(doc: CVDocument) -> Response:
    """Serve a CVDocument's bytes from wherever it actually lives. Shared by
    the admin download endpoint and the user's own /cv/me/download."""
    if doc.storage_backend == "b2":
        try:
            data, content_type = await fetch_b2_object(doc.blob_url)
        except ClientError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found in storage")
        return Response(
            content=data,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
        )

    path = local_file_path(doc.blob_url)
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found in storage")
    return FileResponse(path, filename=doc.filename)


async def parse_cv(db: AsyncSession, cv_id: str) -> None:
    """Background task: download blob, send text to Gemini, store structured JSON.

    TODO: implement blob download + genai client call that returns
    JSON (skills, years_experience, roles). See chat/service.py for the client.
    """
    doc = await db.get(CVDocument, cv_id)
    if not doc:
        return
    doc.parsed = {"skills": [], "years_experience": None, "note": "parsing stub"}
    doc.status = "parsed"
    await db.commit()
