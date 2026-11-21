class ParkingException(Exception):
    """Base class for all domain exceptions."""


class SpotNotFoundException(ParkingException):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Parking spot '{identifier}' not found.")


class NoSpotsAvailableException(ParkingException):
    def __init__(self, spot_type: str) -> None:
        super().__init__(f"No free spots available for type '{spot_type}'.")


class DuplicateActiveTicketException(ParkingException):
    def __init__(self, license_plate: str) -> None:
        super().__init__(
            f"Vehicle '{license_plate}' already has an active parking ticket."
        )


class TicketNotFoundException(ParkingException):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Ticket '{identifier}' not found.")


class TicketAlreadyPaidException(ParkingException):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Ticket '{identifier}' has already been paid.")


class InvalidLicensePlateException(ParkingException):
    def __init__(self, plate: str) -> None:
        super().__init__(
            f"License plate '{plate}' is invalid. Must be non-empty and alphanumeric."
        )
