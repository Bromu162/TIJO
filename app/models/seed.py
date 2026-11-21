from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums import SpotStatus, SpotType
from app.models.spot import Spot


_INITIAL_SPOTS: list[tuple[str, SpotType, int]] = [
    # (spot_number, spot_type, floor)
    ("S-01", SpotType.STANDARD, 0),
    ("S-02", SpotType.STANDARD, 0),
    ("S-03", SpotType.STANDARD, 0),
    ("S-04", SpotType.STANDARD, 0),
    ("S-05", SpotType.STANDARD, 0),
    ("S-06", SpotType.STANDARD, 0),
    ("S-07", SpotType.STANDARD, 1),
    ("S-08", SpotType.STANDARD, 1),
    ("S-09", SpotType.STANDARD, 1),
    ("S-10", SpotType.STANDARD, 1),
    ("S-11", SpotType.STANDARD, 1),
    ("S-12", SpotType.STANDARD, 1),
    ("V-01", SpotType.VIP, 0),
    ("V-02", SpotType.VIP, 0),
    ("V-03", SpotType.VIP, 1),
    ("V-04", SpotType.VIP, 1),
    ("E-01", SpotType.ELECTRIC, 0),
    ("E-02", SpotType.ELECTRIC, 0),
    ("E-03", SpotType.ELECTRIC, 1),
    ("E-04", SpotType.ELECTRIC, 1),
    ("D-01", SpotType.DISABLED, 0),
    ("D-02", SpotType.DISABLED, 0),
    ("D-03", SpotType.DISABLED, 1),
    ("D-04", SpotType.DISABLED, 1),
]


def seed_initial_spots(db: Session) -> None:
    if db.query(Spot).count() > 0:
        return

    now = datetime.now(timezone.utc)
    spots = [
        Spot(
            spot_number=number,
            spot_type=spot_type,
            status=SpotStatus.FREE,
            floor=floor,
            created_at=now,
        )
        for number, spot_type, floor in _INITIAL_SPOTS
    ]
    db.add_all(spots)
    db.commit()
