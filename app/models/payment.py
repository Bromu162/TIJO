from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PaymentMethod


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tickets.id"), nullable=False, unique=True
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False
    )
    payment_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    ticket: Mapped["Ticket"] = relationship(  # type: ignore[name-defined]
        "Ticket", back_populates="payment"
    )

    def __repr__(self) -> str:
        return f"<Payment ticket_id={self.ticket_id} amount={self.amount}>"
