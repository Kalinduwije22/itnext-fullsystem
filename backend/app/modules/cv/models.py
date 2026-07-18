from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base import Base, TimestampMixin, new_uuid


class CVDocument(Base, TimestampMixin):
    __tablename__ = "cv_documents"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    blob_url: Mapped[str]
    filename: Mapped[str]
    status: Mapped[str] = mapped_column(default="uploaded")  # uploaded|parsed|failed
    parsed: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Which storage backend blob_url actually lives in ("local"|"b2"), fixed
    # at upload time — download must never re-derive this from whatever the
    # CURRENT config happens to be, or files uploaded under a since-changed
    # backend become unreachable (see cv/service.py::get_download_target).
    storage_backend: Mapped[str] = mapped_column(default="local")
    # The latest CV for its user. Re-uploading flips the prior row(s) to
    # False rather than deleting them, so admins keep a full history.
    is_current: Mapped[bool] = mapped_column(default=True, server_default="true", index=True)
    grade_score: Mapped[int | None] = mapped_column(nullable=True)
    grade_feedback: Mapped[str | None] = mapped_column(nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Flips False when an admin grades this CV, True once the user dismisses
    # the notification banner. Defaults True so an ungraded CV shows nothing.
    grade_acknowledged: Mapped[bool] = mapped_column(default=True, server_default="true")
