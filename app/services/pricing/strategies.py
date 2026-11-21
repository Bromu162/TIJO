import math
from decimal import Decimal
from datetime import timedelta

from app.models.enums import SpotType
from app.services.pricing.strategy import PricingStrategy


class BasePricingStrategy(PricingStrategy):
    """Shared billing logic: ceil-per-hour with a 24h daily cap."""

    def calculate_fee(self, billable_duration: timedelta) -> Decimal:
        if billable_duration.total_seconds() <= 0:
            return Decimal("0.00")

        total_seconds = billable_duration.total_seconds()
        full_days = int(total_seconds // 86400)
        remaining_seconds = total_seconds % 86400
        remaining_hours = math.ceil(remaining_seconds / 3600) if remaining_seconds > 0 else 0

        daily_fee = self.hourly_rate * 24
        per_day_charge = min(daily_fee, self.daily_cap)

        remaining_fee = self.hourly_rate * remaining_hours
        remaining_charge = min(remaining_fee, self.daily_cap)

        return (per_day_charge * full_days + remaining_charge).quantize(Decimal("0.01"))


class StandardPricingStrategy(BasePricingStrategy):
    spot_type = SpotType.STANDARD
    hourly_rate = Decimal("5.00")
    daily_cap = Decimal("45.00")


class VipPricingStrategy(BasePricingStrategy):
    spot_type = SpotType.VIP
    hourly_rate = Decimal("12.00")
    daily_cap = Decimal("90.00")


class ElectricPricingStrategy(BasePricingStrategy):
    spot_type = SpotType.ELECTRIC
    hourly_rate = Decimal("8.00")
    daily_cap = Decimal("65.00")


class DisabledPricingStrategy(BasePricingStrategy):
    spot_type = SpotType.DISABLED
    hourly_rate = Decimal("2.50")
    daily_cap = Decimal("20.00")
