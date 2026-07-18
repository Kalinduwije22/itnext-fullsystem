"""Read-only queries for the admin dashboard.

No new tables — just joins over User/Order/CVDocument, owned by their
respective modules.
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.schemas import AdminCVOut, AdminOrderOut, AdminStatsOut
from app.modules.auth.models import User
from app.modules.cv.models import CVDocument
from app.modules.payments.models import Order


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.scalars(select(User).order_by(User.created_at.desc()))
    return list(result)


async def list_orders(db: AsyncSession) -> list[AdminOrderOut]:
    rows = await db.execute(
        select(Order, User.email)
        .join(User, User.id == Order.user_id)
        .order_by(Order.created_at.desc())
    )
    return [
        AdminOrderOut(
            id=order.id,
            user_id=order.user_id,
            user_email=email,
            package_id=order.package_id,
            amount_lkr=float(order.amount_lkr),
            status=order.status,
            created_at=order.created_at,
        )
        for order, email in rows.all()
    ]


async def list_cvs(db: AsyncSession) -> list[AdminCVOut]:
    rows = await db.execute(
        select(CVDocument, User.email)
        .join(User, User.id == CVDocument.user_id)
        .order_by(CVDocument.created_at.desc())
    )
    return [
        AdminCVOut(
            id=doc.id,
            user_id=doc.user_id,
            user_email=email,
            filename=doc.filename,
            status=doc.status,
            created_at=doc.created_at,
            grade_score=doc.grade_score,
            grade_feedback=doc.grade_feedback,
            graded_at=doc.graded_at,
        )
        for doc, email in rows.all()
    ]


async def grade_cv(db: AsyncSession, cv_id: str, score: int, feedback: str) -> AdminCVOut:
    row = await db.execute(
        select(CVDocument, User.email)
        .join(User, User.id == CVDocument.user_id)
        .where(CVDocument.id == cv_id)
    )
    result = row.first()
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "CV not found")
    doc, email = result

    doc.grade_score = score
    doc.grade_feedback = feedback
    doc.graded_at = datetime.now(timezone.utc)
    doc.grade_acknowledged = False
    await db.commit()

    return AdminCVOut(
        id=doc.id,
        user_id=doc.user_id,
        user_email=email,
        filename=doc.filename,
        status=doc.status,
        created_at=doc.created_at,
        grade_score=doc.grade_score,
        grade_feedback=doc.grade_feedback,
        graded_at=doc.graded_at,
    )


async def get_stats(db: AsyncSession) -> AdminStatsOut:
    total_users = await db.scalar(select(func.count(User.id))) or 0
    total_orders = await db.scalar(select(func.count(Order.id))) or 0
    paid_orders = await db.scalar(
        select(func.count(Order.id)).where(Order.status == "paid")
    ) or 0
    total_cvs = await db.scalar(select(func.count(CVDocument.id))) or 0
    revenue_lkr = await db.scalar(
        select(func.coalesce(func.sum(Order.amount_lkr), 0)).where(Order.status == "paid")
    ) or 0
    return AdminStatsOut(
        total_users=total_users,
        total_orders=total_orders,
        paid_orders=paid_orders,
        total_cvs=total_cvs,
        revenue_lkr=float(revenue_lkr),
    )
