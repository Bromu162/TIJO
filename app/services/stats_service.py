from sqlalchemy.orm import Session

from app.models.enums import SpotStatus, SpotType
from app.repositories.payment_repository import PaymentRepository
from app.repositories.spot_repository import SpotRepository
from app.repositories.ticket_repository import TicketRepository


class StatsService:
    def __init__(
        self,
        spot_repo: SpotRepository,
        ticket_repo: TicketRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        self._spots = spot_repo
        self._tickets = ticket_repo
        self._payments = payment_repo

    def occupancy_summary(self) -> dict:
        total = len(self._spots.list_all())
        occupied = self._spots.count_by_status(SpotStatus.OCCUPIED)
        free = total - occupied
        occupancy_rate = round((occupied / total * 100), 1) if total > 0 else 0.0

        by_type: dict[str, dict] = {}
        for spot_type in SpotType:
            type_total = len(self._spots.list_by_type(spot_type))
            type_occupied = self._spots.count_by_type_and_status(
                spot_type, SpotStatus.OCCUPIED
            )
            by_type[spot_type.value] = {
                "total": type_total,
                "occupied": type_occupied,
                "free": type_total - type_occupied,
            }

        return {
            "total_spots": total,
            "occupied": occupied,
            "free": free,
            "occupancy_rate_percent": occupancy_rate,
            "by_type": by_type,
        }

    def revenue_summary(self) -> dict:
        total = self._payments.total_revenue()
        by_method = self._payments.revenue_by_method()
        payment_count = self._payments.count_payments()
        completed_tickets = len(self._tickets.list_history(limit=10000))

        return {
            "total_revenue": round(total, 2),
            "payment_count": payment_count,
            "completed_tickets": completed_tickets,
            "revenue_by_method": by_method,
        }
