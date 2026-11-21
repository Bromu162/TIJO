from sqlalchemy.orm import Session

from app.models.enums import SpotStatus, SpotType
from app.models.spot import Spot


class SpotRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, spot_id: int) -> Spot | None:
        return self._db.get(Spot, spot_id)

    def get_by_number(self, spot_number: str) -> Spot | None:
        return (
            self._db.query(Spot)
            .filter(Spot.spot_number == spot_number)
            .first()
        )

    def list_all(self) -> list[Spot]:
        return self._db.query(Spot).order_by(Spot.spot_number).all()

    def list_by_type(self, spot_type: SpotType) -> list[Spot]:
        return (
            self._db.query(Spot)
            .filter(Spot.spot_type == spot_type)
            .order_by(Spot.spot_number)
            .all()
        )

    def list_free_by_type(self, spot_type: SpotType) -> list[Spot]:
        return (
            self._db.query(Spot)
            .filter(Spot.spot_type == spot_type, Spot.status == SpotStatus.FREE)
            .order_by(Spot.spot_number)
            .all()
        )

    def list_by_status(self, status: SpotStatus) -> list[Spot]:
        return (
            self._db.query(Spot)
            .filter(Spot.status == status)
            .order_by(Spot.spot_number)
            .all()
        )

    def count_by_status(self, status: SpotStatus) -> int:
        return self._db.query(Spot).filter(Spot.status == status).count()

    def count_by_type_and_status(self, spot_type: SpotType, status: SpotStatus) -> int:
        return (
            self._db.query(Spot)
            .filter(Spot.spot_type == spot_type, Spot.status == status)
            .count()
        )

    def set_status(self, spot: Spot, status: SpotStatus) -> Spot:
        spot.status = status
        self._db.commit()
        self._db.refresh(spot)
        return spot
