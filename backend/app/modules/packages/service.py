from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.packages.models import Package


async def list_active(db: AsyncSession) -> list[Package]:
    return list(await db.scalars(select(Package).where(Package.is_active.is_(True))))
