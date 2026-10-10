"""Shared exception hierarchy. Services raise these; the console shows the message."""


class ParkingError(Exception):
    """Base class for every Smart Parking domain error."""


class InvalidPlateError(ParkingError):
    """Number plate is missing or not in a valid Indian format."""


class DuplicateEntryError(ParkingError):
    """Vehicle with this plate is already parked in the lot."""


class LotFullError(ParkingError):
    """No suitable free slot exists for this vehicle type."""


class UnpaidTicketError(ParkingError):
    """Ticket has an amount due that has not been paid."""


class ReservationError(ParkingError):
    """Reservation is unknown, expired, cancelled or already used."""


class PaymentError(ParkingError):
    """Payment amount is wrong or the gateway declined it."""
