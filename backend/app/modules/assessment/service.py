from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessment.models import Assessment


async def upsert(db: AsyncSession, user_id: str, answers: dict) -> Assessment:
    existing = await db.scalar(
        select(Assessment).where(Assessment.user_id == user_id)
    )
    if existing:
        existing.answers = answers
        await db.flush()
        return existing
    row = Assessment(user_id=user_id, answers=answers)
    db.add(row)
    await db.flush()
    return row
