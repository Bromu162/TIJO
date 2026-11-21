from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import SpotStatus, SpotType


class Spot(Base):
    __tablename__ = "spots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    spot_number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    spot_type: Mapped[SpotType] = mapped_column(Enum(SpotType), nullable=False)
    status: Mapped[SpotStatus] = mapped_column(
        Enum(SpotStatus), nullable=False, default=SpotStatus.FREE
    )
    floor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<Spot {self.spot_number} [{self.spot_type}] {self.status}>"
