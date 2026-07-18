from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CheckoutIn(BaseModel):
    package_id: str


class CheckoutOut(BaseModel):
    order_id: str
    amount_lkr: float
    # Fields the frontend forwards to PayHere's hosted checkout form.
    merchant_id: str
    return_url: str
    notify_url: str


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    package_id: str
    amount_lkr: float
    status: str
    created_at: datetime
