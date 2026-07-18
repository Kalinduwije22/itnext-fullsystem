from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.cv import service
from app.modules.cv.schemas import CVOut
from app.modules.payments.service import require_paid_user
from app.shared.deps import get_current_user

router = APIRouter(prefix="/cv", tags=["cv"])


@router.get("/me", response_model=CVOut | None)
async def my_cv(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await service.get_current_cv(db, user.id)


@router.get("/me/download")
async def download_my_cv(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    doc = await service.get_current_cv(db, user.id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No CV uploaded yet")
    return await service.build_download_response(doc)


@router.post("/me/acknowledge", response_model=CVOut)
async def acknowledge_my_grade(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    doc = await service.get_current_cv(db, user.id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No CV uploaded yet")
    return await service.acknowledge_grade(db, doc.id, user.id)


@router.post("/upload", response_model=CVOut)
async def upload(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(require_paid_user),
    db: AsyncSession = Depends(get_db),
):
    data = await file.read()
    doc = await service.upload_and_record(db, user.id, file.filename or "cv", data)
    # Parsing runs after the response is returned. Swap BackgroundTasks for a
    # Celery task when parsing volume grows.
    background.add_task(service.parse_cv, db, doc.id)
    return doc
