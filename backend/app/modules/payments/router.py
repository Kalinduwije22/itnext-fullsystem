from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.payments import service
from app.modules.payments.schemas import CheckoutIn, CheckoutOut, OrderOut
from app.shared.deps import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/orders", response_model=list[OrderOut])
async def my_orders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_my_orders(db, user.id)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def order_detail(
    order_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_order(db, user.id, order_id)


@router.post("/checkout", response_model=CheckoutOut)
async def checkout(
    data: CheckoutIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await service.create_checkout(db, user.id, data.package_id)
    return CheckoutOut(
        order_id=order.id,
        amount_lkr=float(order.amount_lkr),
        merchant_id=settings.payhere_merchant_id,
        return_url="https://itnextglobalcareers.com/payment/return",
        notify_url="https://api.itnextglobalcareers.com/api/v1/payments/notify",
    )


@router.post("/orders/{order_id}/simulate-paid", response_model=OrderOut)
async def simulate_paid(
    order_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dev-only stand-in for PayHere's webhook, so the paid flow can be
    tested end-to-end without a PayHere sandbox account. Never available
    once ENVIRONMENT=production, and only ever affects an order the caller
    themselves owns (get_order 404s otherwise)."""
    if settings.environment == "production":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    order = await service.get_order(db, user.id, order_id)
    await service.handle_webhook(db, order.id, "2")
    return await service.get_order(db, user.id, order_id)


@router.post("/notify")
async def notify(
    order_id: str = Form(..., alias="order_id"),
    status_code: str = Form(..., alias="status_code"),
    payhere_amount: str = Form(default=""),
    payhere_currency: str = Form(default=""),
    md5sig: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
):
    # Public endpoint hit by PayHere's servers — no auth, must verify signature.
    await service.handle_webhook(
        db,
        order_id,
        status_code,
        amount=payhere_amount,
        currency=payhere_currency,
        md5sig=md5sig,
    )
    return {"received": True}
