from datetime import datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import PaymentMethod, SpotType, TicketStatus
from app.schemas.spot import SpotRead


class TicketEntryRequest(BaseModel):
    license_plate: str
    spot_type: SpotType


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_code: str
    license_plate: str
    spot_id: int
    spot_type: SpotType
    entry_time: datetime
    exit_time: datetime | None
    status: TicketStatus
    total_amount: float | None
    spot: SpotRead | None = None


class FeePreviewResponse(BaseModel):
    ticket_id: int
    ticket_code: str
    license_plate: str
    spot_type: SpotType
    entry_time: datetime
    total_duration_minutes: float
    billable_duration_minutes: float
    grace_period_applied: bool
    charged_hours: int
    hourly_rate: Decimal
    daily_cap: Decimal
    estimated_fee: Decimal


class TicketExitRequest(BaseModel):
    payment_method: PaymentMethod = PaymentMethod.CARD
