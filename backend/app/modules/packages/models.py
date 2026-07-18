from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base import Base, TimestampMixin, new_uuid


class Package(Base, TimestampMixin):
    """A purchasable tier (Starter, Professional, Premium, VIP)."""
    __tablename__ = "packages"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    price_lkr: Mapped[float] = mapped_column(Numeric(12, 2))
    description: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
