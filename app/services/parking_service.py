import re
from datetime import datetime

from app.core.exceptions import (
    DuplicateActiveTicketException,
    InvalidLicensePlateException,
    NoSpotsAvailableException,
    TicketAlreadyPaidException,
    TicketNotFoundException,
)
from app.core.time_provider import TimeProvider
from app.models.enums import PaymentMethod, SpotStatus, SpotType, TicketStatus
from app.models.payment import Payment
from app.models.ticket import Ticket
from app.repositories.payment_repository import PaymentRepository
from app.repositories.spot_repository import SpotRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.pricing.calculator import FeeBreakdown, PricingCalculator

_LICENSE_PLATE_PATTERN = re.compile(r"^[A-Z0-9]{2,10}$")


def _generate_ticket_code(entry_time: datetime, ticket_id: int) -> str:
    date_part = entry_time.strftime("%Y%m%d")
    return f"TCK-{date_part}-{ticket_id:04d}"


class ParkingService:
    def __init__(
        self,
        spot_repo: SpotRepository,
        ticket_repo: TicketRepository,
        payment_repo: PaymentRepository,
        pricing_calculator: PricingCalculator,
        time_provider: TimeProvider,
    ) -> None:
        self._spots = spot_repo
        self._tickets = ticket_repo
        self._payments = payment_repo
        self._calculator = pricing_calculator
        self._time = time_provider

    def _validate_license_plate(self, raw_plate: str) -> str:
        normalized = raw_plate.strip().upper().replace(" ", "").replace("-", "")
        if not _LICENSE_PLATE_PATTERN.match(normalized):
            raise InvalidLicensePlateException(raw_plate)
        return normalized

    def register_entry(self, license_plate: str, spot_type: SpotType) -> Ticket:
        plate = self._validate_license_plate(license_plate)

        existing = self._tickets.get_active_by_plate(plate)
        if existing is not None:
            raise DuplicateActiveTicketException(plate)

        free_spots = self._spots.list_free_by_type(spot_type)
        if not free_spots:
            raise NoSpotsAvailableException(spot_type.value)

        chosen_spot = free_spots[0]
        entry_time = self._time.now()

        ticket = Ticket(
            ticket_code="PENDING",
            license_plate=plate,
            spot_id=chosen_spot.id,
            spot_type=spot_type,
            entry_time=entry_time,
            status=TicketStatus.ACTIVE,
        )
        saved = self._tickets.save(ticket)

        saved.ticket_code = _generate_ticket_code(entry_time, saved.id)
        self._spots.set_status(chosen_spot, SpotStatus.OCCUPIED)
        updated = self._tickets.update(saved)

        return updated

    def calculate_fee(self, ticket_id: int) -> tuple[Ticket, FeeBreakdown]:
        ticket = self._tickets.get_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundException(str(ticket_id))
        if ticket.status != TicketStatus.ACTIVE:
            raise TicketAlreadyPaidException(ticket.ticket_code)

        breakdown = self._calculator.calculate(
            spot_type=ticket.spot_type,
            entry_time=ticket.entry_time,
        )
        return ticket, breakdown

    def register_exit(
        self, ticket_id: int, payment_method: PaymentMethod
    ) -> tuple[Ticket, Payment | None]:
        ticket, breakdown = self.calculate_fee(ticket_id)

        exit_time = self._time.now()
        ticket.exit_time = exit_time
        ticket.status = TicketStatus.PAID
        ticket.total_amount = float(breakdown.total_fee)

        self._spots.set_status(ticket.spot, SpotStatus.FREE)
        self._tickets.update(ticket)

        payment = None
        if breakdown.total_fee > 0:
            payment = Payment(
                ticket_id=ticket.id,
                amount=float(breakdown.total_fee),
                payment_method=payment_method,
                payment_time=exit_time,
            )
            self._payments.save(payment)

        return ticket, payment
