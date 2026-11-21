from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import PaymentMethod
from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, payment: Payment) -> Payment:
        self._db.add(payment)
        self._db.commit()
        self._db.refresh(payment)
        return payment

    def total_revenue(self) -> float:
        result = self._db.query(func.sum(Payment.amount)).scalar()
        return float(result) if result is not None else 0.0

    def revenue_by_method(self) -> dict[str, float]:
        rows = (
            self._db.query(Payment.payment_method, func.sum(Payment.amount))
            .group_by(Payment.payment_method)
            .all()
        )
        return {method.value: float(total) for method, total in rows}

    def list_recent(self, limit: int = 50) -> list[Payment]:
        return (
            self._db.query(Payment)
            .order_by(Payment.payment_time.desc())
            .limit(limit)
            .all()
        )

    def count_payments(self) -> int:
        return self._db.query(Payment).count()
