from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.modules.auth.models import User
from app.modules.payments import service
from app.shared.deps import get_current_user

client = TestClient(app)


class _FakeOrder:
    def __init__(self, id_, user_id, status="pending"):
        self.id = id_
        self.user_id = user_id
        self.package_id = "pkg-1"
        self.amount_lkr = 29900
        self.status = status
        from datetime import datetime, timezone

        self.created_at = datetime.now(timezone.utc)


class _FakeDB:
    def __init__(self, order):
        self._order = order

    async def get(self, _model, _id):
        return self._order

    async def commit(self):
        pass


def _user():
    return User(
        id="user-1",
        email="user@example.com",
        full_name="U",
        hashed_password="x",
        is_active=True,
        is_admin=False,
    )


def teardown_function(_fn):
    app.dependency_overrides.clear()
    settings.environment = "development"


def test_simulate_paid_marks_own_order_paid():
    order = _FakeOrder("order-1", "user-1")

    async def _override_db():
        yield _FakeDB(order)

    app.dependency_overrides[get_current_user] = _user
    app.dependency_overrides[get_db] = _override_db

    resp = client.post("/api/v1/payments/orders/order-1/simulate-paid")
    assert resp.status_code == 200
    assert order.status == "paid"


def test_simulate_paid_404s_for_someone_elses_order():
    order = _FakeOrder("order-1", "someone-else")

    async def _override_db():
        yield _FakeDB(order)

    app.dependency_overrides[get_current_user] = _user
    app.dependency_overrides[get_db] = _override_db

    resp = client.post("/api/v1/payments/orders/order-1/simulate-paid")
    assert resp.status_code == 404
    assert order.status == "pending"


def test_simulate_paid_disabled_in_production():
    settings.environment = "production"
    order = _FakeOrder("order-1", "user-1")

    async def _override_db():
        yield _FakeDB(order)

    app.dependency_overrides[get_current_user] = _user
    app.dependency_overrides[get_db] = _override_db

    resp = client.post("/api/v1/payments/orders/order-1/simulate-paid")
    assert resp.status_code == 404
    assert order.status == "pending"
