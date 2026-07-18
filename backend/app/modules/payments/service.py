"""Order creation + PayHere webhook confirmation.

Card data NEVER touches this backend. The frontend redirects to PayHere's
hosted checkout; PayHere calls our notify_url (webhook) to confirm payment,
and only then do we mark the order paid.
"""
import hashlib
import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.packages.models import Package
from app.modules.payments.models import Order
from app.shared.deps import get_current_user

logger = logging.getLogger(__name__)


async def create_checkout(db: AsyncSession, user_id: str, package_id: str) -> Order:
    package = await db.get(Package, package_id)
    if not package:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Package not found")
    order = Order(
        user_id=user_id,
        package_id=package_id,
        amount_lkr=package.price_lkr,
    )
    db.add(order)
    await db.flush()
    return order


def verify_payhere_signature(
    merchant_id: str, order_id: str, amount: str, currency: str, status_code: str, md5sig: str
) -> bool:
    """PayHere's documented notify-webhook signature check.

    local_md5sig = strtoupper(md5(merchant_id + order_id + amount + currency +
                   status_code + strtoupper(md5(merchant_secret))))
    """
    secret_hash = hashlib.md5(settings.payhere_merchant_secret.encode()).hexdigest().upper()
    local = hashlib.md5(
        f"{merchant_id}{order_id}{amount}{currency}{status_code}{secret_hash}".encode()
    ).hexdigest().upper()
    return local == md5sig.upper()


async def handle_webhook(
    db: AsyncSession,
    order_id: str,
    payhere_status: str,
    *,
    amount: str = "",
    currency: str = "",
    md5sig: str = "",
) -> None:
    """Called by PayHere's server-to-server notification.

    Signature verification is skipped (with a warning) when no merchant
    secret is configured, so the app keeps booting/testing with zero
    external credentials, same as every other stub in this codebase.
    """
    if settings.payhere_merchant_secret:
        if not verify_payhere_signature(
            settings.payhere_merchant_id, order_id, amount, currency, payhere_status, md5sig
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook signature")
    else:
        logger.warning("PAYHERE_MERCHANT_SECRET not set — skipping webhook signature check")

    order = await db.get(Order, order_id)
    if not order:
        return
    order.status = "paid" if payhere_status == "2" else "failed"
    await db.commit()


async def has_paid_order(db: AsyncSession, user_id: str) -> bool:
    result = await db.scalar(
        select(Order.id).where(Order.user_id == user_id, Order.status == "paid").limit(1)
    )
    return result is not None


async def require_paid_user(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not await has_paid_order(db, user.id):
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED,
            "Complete a package purchase before uploading a CV",
        )
    return user


async def list_my_orders(db: AsyncSession, user_id: str) -> list[Order]:
    result = await db.scalars(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    return list(result)


async def get_order(db: AsyncSession, user_id: str, order_id: str) -> Order:
    order = await db.get(Order, order_id)
    if not order or order.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return order
