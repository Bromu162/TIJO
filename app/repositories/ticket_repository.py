from sqlalchemy.orm import Session

from app.models.enums import TicketStatus
from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self._db.get(Ticket, ticket_id)

    def get_by_code(self, ticket_code: str) -> Ticket | None:
        return (
            self._db.query(Ticket)
            .filter(Ticket.ticket_code == ticket_code)
            .first()
        )

    def get_active_by_plate(self, license_plate: str) -> Ticket | None:
        return (
            self._db.query(Ticket)
            .filter(
                Ticket.license_plate == license_plate,
                Ticket.status == TicketStatus.ACTIVE,
            )
            .first()
        )

    def list_active(self) -> list[Ticket]:
        return (
            self._db.query(Ticket)
            .filter(Ticket.status == TicketStatus.ACTIVE)
            .order_by(Ticket.entry_time.desc())
            .all()
        )

    def list_history(self, limit: int = 100) -> list[Ticket]:
        return (
            self._db.query(Ticket)
            .filter(Ticket.status != TicketStatus.ACTIVE)
            .order_by(Ticket.exit_time.desc())
            .limit(limit)
            .all()
        )

    def save(self, ticket: Ticket) -> Ticket:
        self._db.add(ticket)
        self._db.commit()
        self._db.refresh(ticket)
        return ticket

    def update(self, ticket: Ticket) -> Ticket:
        self._db.commit()
        self._db.refresh(ticket)
        return ticket
