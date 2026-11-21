from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import SpotType, TicketStatus

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.spot import Spot


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    license_plate: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    spot_id: Mapped[int] = mapped_column(Integer, ForeignKey("spots.id"), nullable=False)
    spot_type: Mapped[SpotType] = mapped_column(Enum(SpotType), nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus), nullable=False, default=TicketStatus.ACTIVE
    )
    total_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    spot: Mapped["Spot"] = relationship("Spot", lazy="joined")  # type: ignore[name-defined]
    payment: Mapped["Payment | None"] = relationship(  # type: ignore[name-defined]
        "Payment", back_populates="ticket", uselist=False, lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_code} [{self.license_plate}] {self.status}>"
