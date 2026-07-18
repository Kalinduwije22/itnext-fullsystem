from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.admin import service
from app.modules.admin.schemas import (
    AdminCVOut,
    AdminOrderOut,
    AdminStatsOut,
    AdminUserOut,
    GradeCVRequest,
)
from app.modules.cv import service as cv_service
from app.modules.cv.models import CVDocument
from app.shared.deps import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin_user)])


@router.get("/stats", response_model=AdminStatsOut)
async def stats(db: AsyncSession = Depends(get_db)):
    return await service.get_stats(db)


@router.get("/users", response_model=list[AdminUserOut])
async def users(db: AsyncSession = Depends(get_db)):
    return await service.list_users(db)


@router.get("/orders", response_model=list[AdminOrderOut])
async def orders(db: AsyncSession = Depends(get_db)):
    return await service.list_orders(db)


@router.get("/cvs", response_model=list[AdminCVOut])
async def cvs(db: AsyncSession = Depends(get_db)):
    return await service.list_cvs(db)


@router.get("/cvs/{cv_id}/download")
async def download_cv(cv_id: str, db: AsyncSession = Depends(get_db)):
    doc = await db.get(CVDocument, cv_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "CV not found")
    return await cv_service.build_download_response(doc)


@router.patch("/cvs/{cv_id}/grade", response_model=AdminCVOut)
async def grade_cv(cv_id: str, data: GradeCVRequest, db: AsyncSession = Depends(get_db)):
    return await service.grade_cv(db, cv_id, data.score, data.feedback)
