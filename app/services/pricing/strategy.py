from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import timedelta

from app.models.enums import SpotType


class PricingStrategy(ABC):
    """Base interface for all spot-type pricing strategies."""

    spot_type: SpotType
    hourly_rate: Decimal
    daily_cap: Decimal

    @abstractmethod
    def calculate_fee(self, billable_duration: timedelta) -> Decimal:
        """
        Calculate the parking fee for the given billable duration.
        The duration passed here already excludes any grace period.
        """
