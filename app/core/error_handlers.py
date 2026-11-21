from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DuplicateActiveTicketException,
    InvalidLicensePlateException,
    NoSpotsAvailableException,
    ParkingException,
    SpotNotFoundException,
    TicketAlreadyPaidException,
    TicketNotFoundException,
)


def _error_response(status_code: int, detail: str, error_code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "error_code": error_code},
    )


async def spot_not_found_handler(
    _request: Request, exc: SpotNotFoundException
) -> JSONResponse:
    return _error_response(404, str(exc), "SPOT_NOT_FOUND")


async def ticket_not_found_handler(
    _request: Request, exc: TicketNotFoundException
) -> JSONResponse:
    return _error_response(404, str(exc), "TICKET_NOT_FOUND")


async def no_spots_available_handler(
    _request: Request, exc: NoSpotsAvailableException
) -> JSONResponse:
    return _error_response(409, str(exc), "NO_SPOTS_AVAILABLE")


async def duplicate_ticket_handler(
    _request: Request, exc: DuplicateActiveTicketException
) -> JSONResponse:
    return _error_response(409, str(exc), "DUPLICATE_ACTIVE_TICKET")


async def ticket_already_paid_handler(
    _request: Request, exc: TicketAlreadyPaidException
) -> JSONResponse:
    return _error_response(409, str(exc), "TICKET_ALREADY_PAID")


async def invalid_plate_handler(
    _request: Request, exc: InvalidLicensePlateException
) -> JSONResponse:
    return _error_response(400, str(exc), "INVALID_LICENSE_PLATE")


async def generic_parking_handler(
    _request: Request, exc: ParkingException
) -> JSONResponse:
    return _error_response(400, str(exc), "PARKING_ERROR")


def register_error_handlers(app) -> None:  # type: ignore[no-untyped-def]
    app.add_exception_handler(SpotNotFoundException, spot_not_found_handler)
    app.add_exception_handler(TicketNotFoundException, ticket_not_found_handler)
    app.add_exception_handler(NoSpotsAvailableException, no_spots_available_handler)
    app.add_exception_handler(
        DuplicateActiveTicketException, duplicate_ticket_handler
    )
    app.add_exception_handler(TicketAlreadyPaidException, ticket_already_paid_handler)
    app.add_exception_handler(
        InvalidLicensePlateException, invalid_plate_handler
    )
    app.add_exception_handler(ParkingException, generic_parking_handler)
