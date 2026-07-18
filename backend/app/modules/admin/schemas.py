from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    phone: str | None = None
    is_admin: bool
    is_active: bool
    created_at: datetime


class AdminOrderOut(BaseModel):
    id: str
    user_id: str
    user_email: str
    package_id: str
    amount_lkr: float
    status: str
    created_at: datetime


class AdminCVOut(BaseModel):
    id: str
    user_id: str
    user_email: str
    filename: str
    status: str
    created_at: datetime
    grade_score: int | None = None
    grade_feedback: str | None = None
    graded_at: datetime | None = None


class GradeCVRequest(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str = Field(min_length=1)


class AdminStatsOut(BaseModel):
    total_users: int
    total_orders: int
    paid_orders: int
    total_cvs: int
    revenue_lkr: float
