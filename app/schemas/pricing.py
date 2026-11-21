from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import SpotType


class PricingRateRead(BaseModel):
    spot_type: SpotType
    hourly_rate: Decimal
    daily_cap: Decimal


class PricingInfoResponse(BaseModel):
    grace_period_minutes: int
    billing_unit: str
    rates: list[PricingRateRead]
