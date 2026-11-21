from fastapi import APIRouter, Depends

from app.core.dependencies import get_parking_service, get_ticket_repo
from app.repositories.ticket_repository import TicketRepository
from app.schemas.payment import ExitReceiptResponse, PaymentRead
from app.schemas.ticket import (
    FeePreviewResponse,
    TicketEntryRequest,
    TicketExitRequest,
    TicketRead,
)
from app.services.parking_service import ParkingService

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("/entry", response_model=TicketRead, status_code=201)
def register_entry(
    request: TicketEntryRequest,
    service: ParkingService = Depends(get_parking_service),
) -> object:
    return service.register_entry(
        license_plate=request.license_plate,
        spot_type=request.spot_type,
    )


@router.get("/active", response_model=list[TicketRead])
def list_active_tickets(
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
) -> list:
    return ticket_repo.list_active()


@router.get("/history", response_model=list[TicketRead])
def list_ticket_history(
    limit: int = 100,
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
) -> list:
    return ticket_repo.list_history(limit=limit)


@router.get("/{ticket_id}/calculate", response_model=FeePreviewResponse)
def calculate_fee(
    ticket_id: int,
    service: ParkingService = Depends(get_parking_service),
) -> dict:
    ticket, breakdown = service.calculate_fee(ticket_id)
    return {
        "ticket_id": ticket.id,
        "ticket_code": ticket.ticket_code,
        "license_plate": ticket.license_plate,
        "spot_type": ticket.spot_type,
        "entry_time": ticket.entry_time,
        "total_duration_minutes": round(
            breakdown.total_duration.total_seconds() / 60, 2
        ),
        "billable_duration_minutes": round(
            breakdown.billable_duration.total_seconds() / 60, 2
        ),
        "grace_period_applied": breakdown.grace_period_applied,
        "charged_hours": breakdown.charged_hours,
        "hourly_rate": breakdown.hourly_rate,
        "daily_cap": breakdown.daily_cap,
        "estimated_fee": breakdown.total_fee,
    }


@router.post("/{ticket_id}/pay", response_model=ExitReceiptResponse)
def register_exit(
    ticket_id: int,
    request: TicketExitRequest,
    service: ParkingService = Depends(get_parking_service),
) -> dict:
    ticket, payment = service.register_exit(ticket_id, request.payment_method)
    return {
        "ticket_id": ticket.id,
        "ticket_code": ticket.ticket_code,
        "license_plate": ticket.license_plate,
        "entry_time": ticket.entry_time,
        "exit_time": ticket.exit_time,
        "total_amount": ticket.total_amount or 0.0,
        "payment": PaymentRead.model_validate(payment) if payment else None,
    }
