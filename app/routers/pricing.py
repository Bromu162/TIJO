from fastapi import APIRouter

from app.core.config import settings
from app.models.enums import SpotType
from app.schemas.pricing import PricingInfoResponse, PricingRateRead
from app.services.pricing.strategies import (
    DisabledPricingStrategy,
    ElectricPricingStrategy,
    StandardPricingStrategy,
    VipPricingStrategy,
)

router = APIRouter(prefix="/api/pricing", tags=["pricing"])

_STRATEGIES = [
    StandardPricingStrategy(),
    VipPricingStrategy(),
    ElectricPricingStrategy(),
    DisabledPricingStrategy(),
]


@router.get("", response_model=PricingInfoResponse)
def get_pricing_info() -> dict:
    rates = [
        PricingRateRead(
            spot_type=s.spot_type,
            hourly_rate=s.hourly_rate,
            daily_cap=s.daily_cap,
        )
        for s in _STRATEGIES
    ]
    return {
        "grace_period_minutes": settings.grace_period_minutes,
        "billing_unit": "per started hour",
        "rates": rates,
    }
