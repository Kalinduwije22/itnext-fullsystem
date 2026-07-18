from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.assessment import service
from app.modules.assessment.schemas import AssessmentIn, AssessmentOut
from app.modules.auth.models import User
from app.shared.deps import get_current_user

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.put("", response_model=AssessmentOut)
async def submit(
    data: AssessmentIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.upsert(db, user.id, data.answers)
