from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import PaymentMethod


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    amount: float
    payment_method: PaymentMethod
    payment_time: datetime


class ExitReceiptResponse(BaseModel):
    ticket_id: int
    ticket_code: str
    license_plate: str
    entry_time: datetime
    exit_time: datetime
    total_amount: float
    payment: PaymentRead | None


class RevenueSummaryResponse(BaseModel):
    total_revenue: float
    payment_count: int
    completed_tickets: int
    revenue_by_method: dict[str, float]
