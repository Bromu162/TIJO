from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_spot_repo, get_stats_service
from app.models.enums import SpotStatus, SpotType
from app.repositories.spot_repository import SpotRepository
from app.schemas.spot import OccupancyStats, SpotRead, SpotTypeStats
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/spots", tags=["spots"])


@router.get("", response_model=list[SpotRead])
def list_spots(
    status: SpotStatus | None = Query(default=None),
    spot_type: SpotType | None = Query(default=None, alias="type"),
    spot_repo: SpotRepository = Depends(get_spot_repo),
) -> list:
    if status and spot_type:
        spots = spot_repo.list_by_type(spot_type)
        return [s for s in spots if s.status == status]
    if status:
        return spot_repo.list_by_status(status)
    if spot_type:
        return spot_repo.list_by_type(spot_type)
    return spot_repo.list_all()


@router.get("/stats", response_model=OccupancyStats)
def occupancy_stats(stats_service: StatsService = Depends(get_stats_service)) -> dict:
    summary = stats_service.occupancy_summary()
    summary["by_type"] = {
        k: SpotTypeStats(**v) for k, v in summary["by_type"].items()
    }
    return summary
