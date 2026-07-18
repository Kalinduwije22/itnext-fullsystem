from datetime import datetime

from pydantic import BaseModel


class CVOut(BaseModel):
    id: str
    filename: str
    status: str
    parsed: dict | None = None
    is_current: bool
    created_at: datetime
    grade_score: int | None = None
    grade_feedback: str | None = None
    graded_at: datetime | None = None
    grade_acknowledged: bool

    class Config:
        from_attributes = True
