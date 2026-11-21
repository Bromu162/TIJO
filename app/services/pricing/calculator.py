from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.config import settings
from app.core.time_provider import TimeProvider
from app.models.enums import SpotType
from app.services.pricing.strategies import (
    DisabledPricingStrategy,
    ElectricPricingStrategy,
    StandardPricingStrategy,
    VipPricingStrategy,
)
from app.services.pricing.strategy import PricingStrategy


@dataclass(frozen=True)
class FeeBreakdown:
    total_duration: timedelta
    billable_duration: timedelta
    grace_period_applied: bool
    charged_hours: int
    hourly_rate: Decimal
    daily_cap: Decimal
    total_fee: Decimal


class PricingCalculator:
    """Calculates parking fees using the Strategy pattern per spot type."""

    _strategies: dict[SpotType, PricingStrategy] = {
        SpotType.STANDARD: StandardPricingStrategy(),
        SpotType.VIP: VipPricingStrategy(),
        SpotType.ELECTRIC: ElectricPricingStrategy(),
        SpotType.DISABLED: DisabledPricingStrategy(),
    }

    def __init__(self, time_provider: TimeProvider) -> None:
        self._time_provider = time_provider

    def get_strategy(self, spot_type: SpotType) -> PricingStrategy:
        return self._strategies[spot_type]

    def calculate(
        self,
        spot_type: SpotType,
        entry_time: datetime,
        exit_time: datetime | None = None,
    ) -> FeeBreakdown:
        resolved_exit = exit_time or self._time_provider.now()

        # Normalize both datetimes to UTC-aware for safe subtraction
        if entry_time.tzinfo is None:
            from datetime import timezone
            entry_time = entry_time.replace(tzinfo=timezone.utc)
        if resolved_exit.tzinfo is None:
            from datetime import timezone
            resolved_exit = resolved_exit.replace(tzinfo=timezone.utc)

        total_duration = resolved_exit - entry_time
        grace = timedelta(minutes=settings.grace_period_minutes)
        grace_applied = total_duration <= grace
        billable_duration = max(total_duration - grace, timedelta(0))

        strategy = self.get_strategy(spot_type)
        fee = strategy.calculate_fee(billable_duration)

        import math
        charged_hours = (
            math.ceil(billable_duration.total_seconds() / 3600)
            if billable_duration.total_seconds() > 0
            else 0
        )

        return FeeBreakdown(
            total_duration=total_duration,
            billable_duration=billable_duration,
            grace_period_applied=grace_applied,
            charged_hours=charged_hours,
            hourly_rate=strategy.hourly_rate,
            daily_cap=strategy.daily_cap,
            total_fee=fee,
        )
