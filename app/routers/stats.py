from fastapi import APIRouter, Depends

from app.core.dependencies import get_stats_service
from app.schemas.payment import RevenueSummaryResponse
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/revenue", response_model=RevenueSummaryResponse)
def revenue_summary(stats_service: StatsService = Depends(get_stats_service)) -> dict:
    return stats_service.revenue_summary()
