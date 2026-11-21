import enum


class SpotType(str, enum.Enum):
    STANDARD = "STANDARD"
    VIP = "VIP"
    ELECTRIC = "ELECTRIC"
    DISABLED = "DISABLED"


class SpotStatus(str, enum.Enum):
    FREE = "FREE"
    OCCUPIED = "OCCUPIED"


class TicketStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    APP = "APP"
