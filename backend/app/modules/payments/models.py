from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base import Base, TimestampMixin, new_uuid


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    package_id: Mapped[str] = mapped_column(ForeignKey("packages.id"))
    amount_lkr: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(default="pending")  # pending|paid|failed
