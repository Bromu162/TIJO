from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import SpotStatus, SpotType


class SpotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    spot_number: str
    spot_type: SpotType
    status: SpotStatus
    floor: int
    created_at: datetime


class SpotTypeStats(BaseModel):
    total: int
    occupied: int
    free: int


class OccupancyStats(BaseModel):
    total_spots: int
    occupied: int
    free: int
    occupancy_rate_percent: float
    by_type: dict[str, SpotTypeStats]
