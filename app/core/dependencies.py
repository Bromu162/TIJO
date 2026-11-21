from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.time_provider import SystemTimeProvider, TimeProvider
from app.repositories.payment_repository import PaymentRepository
from app.repositories.spot_repository import SpotRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.parking_service import ParkingService
from app.services.pricing.calculator import PricingCalculator
from app.services.stats_service import StatsService

from fastapi import Depends


_time_provider: TimeProvider = SystemTimeProvider()


def get_time_provider() -> TimeProvider:
    return _time_provider


def get_spot_repo(db: Session = Depends(get_db)) -> SpotRepository:
    return SpotRepository(db)


def get_ticket_repo(db: Session = Depends(get_db)) -> TicketRepository:
    return TicketRepository(db)


def get_payment_repo(db: Session = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(db)


def get_pricing_calculator(
    time_provider: TimeProvider = Depends(get_time_provider),
) -> PricingCalculator:
    return PricingCalculator(time_provider)


def get_parking_service(
    spot_repo: SpotRepository = Depends(get_spot_repo),
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
    payment_repo: PaymentRepository = Depends(get_payment_repo),
    pricing_calculator: PricingCalculator = Depends(get_pricing_calculator),
    time_provider: TimeProvider = Depends(get_time_provider),
) -> ParkingService:
    return ParkingService(
        spot_repo=spot_repo,
        ticket_repo=ticket_repo,
        payment_repo=payment_repo,
        pricing_calculator=pricing_calculator,
        time_provider=time_provider,
    )


def get_stats_service(
    spot_repo: SpotRepository = Depends(get_spot_repo),
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
    payment_repo: PaymentRepository = Depends(get_payment_repo),
) -> StatsService:
    return StatsService(
        spot_repo=spot_repo,
        ticket_repo=ticket_repo,
        payment_repo=payment_repo,
    )
