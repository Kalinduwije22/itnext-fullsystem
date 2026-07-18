import hashlib

import pytest

from app.core.config import settings
from app.modules.payments import service


class _FakeOrder:
    def __init__(self):
        self.status = "pending"


class _FakeDB:
    def __init__(self, order):
        self._order = order
        self.committed = False

    async def get(self, _model, _id):
        return self._order

    async def commit(self):
        self.committed = True


def test_verify_signature_correct():
    settings.payhere_merchant_secret = "testsecret"
    try:
        secret_hash = hashlib.md5(b"testsecret").hexdigest().upper()
        local = hashlib.md5(
            f"merchant1order1100.00LKR2{secret_hash}".encode()
        ).hexdigest().upper()
        assert service.verify_payhere_signature(
            "merchant1", "order1", "100.00", "LKR", "2", local
        )
    finally:
        settings.payhere_merchant_secret = ""


def test_verify_signature_incorrect():
    settings.payhere_merchant_secret = "testsecret"
    try:
        assert not service.verify_payhere_signature(
            "merchant1", "order1", "100.00", "LKR", "2", "WRONGSIG"
        )
    finally:
        settings.payhere_merchant_secret = ""


@pytest.mark.asyncio
async def test_handle_webhook_skips_verification_when_secret_blank():
    settings.payhere_merchant_secret = ""
    order = _FakeOrder()
    db = _FakeDB(order)
    await service.handle_webhook(db, "order-1", "2")
    assert order.status == "paid"
    assert db.committed


@pytest.mark.asyncio
async def test_handle_webhook_rejects_bad_signature_when_secret_set():
    settings.payhere_merchant_secret = "testsecret"
    try:
        order = _FakeOrder()
        db = _FakeDB(order)
        with pytest.raises(Exception):
            await service.handle_webhook(
                db, "order-1", "2", amount="100.00", currency="LKR", md5sig="WRONG"
            )
        assert order.status == "pending"
    finally:
        settings.payhere_merchant_secret = ""
