from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.packages import service
from app.modules.packages.schemas import PackageOut

router = APIRouter(prefix="/packages", tags=["packages"])


@router.get("", response_model=list[PackageOut])
async def list_packages(db: AsyncSession = Depends(get_db)):
    return await service.list_active(db)
