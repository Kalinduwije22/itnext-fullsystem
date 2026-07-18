from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base import Base, TimestampMixin, new_uuid


class Assessment(Base, TimestampMixin):
    """User's professional-condition questionnaire.

    Answers are stored as JSONB so form questions can change without a schema
    migration — the module owns the shape, the DB just holds it.
    """
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    answers: Mapped[dict] = mapped_column(JSON)
