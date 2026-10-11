"""Vehicle entry and exit (SPMS-F-006..009)."""
import re
import uuid
from datetime import datetime

from smart_parking.allocation import find_slot
from smart_parking.billing import calculate_fee
from smart_parking.errors import (
    DuplicateEntryError,
    InvalidPlateError,
    LotFullError,
    ParkingError,
    UnpaidTicketError,
)
from smart_parking.models import ParkingLot, Ticket, Vehicle

# 2 letters (state), 1-2 digits (RTO), 0-3 letters (series), 4 digits (number)
PLATE_PATTERN = re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{4}$")


def validate_plate(plate) -> bool:
    """Return True if plate is a valid Indian number plate, e.g. KA01AB1234.

    Surrounding whitespace is ignored and letters are compared in upper case.
    """
    if not isinstance(plate, str):
        return False
    return bool(PLATE_PATTERN.match(plate.strip().upper()))


def vehicle_entry(lot: ParkingLot, vehicle: Vehicle, now: datetime, tickets: dict) -> Ticket:
    """Register a vehicle at the entry gate (SPMS-F-007).

    Validates the plate, allocates the best slot, marks it occupied and issues a
    ticket stored in `tickets` under a random UUID.
    Raises InvalidPlateError, DuplicateEntryError (SPMS-F-008) or LotFullError;
    the lot is unchanged on error.
    """
    if not validate_plate(vehicle.plate):
        raise InvalidPlateError(f"Invalid number plate: {vehicle.plate!r}")
    plate = vehicle.plate.strip().upper()
    if any(s.occupied_by == plate for s in lot.slots):
        raise DuplicateEntryError(f"Vehicle {plate} is already parked")
    slot = find_slot(lot, vehicle)
    if slot is None:
        raise LotFullError(f"Lot full for {vehicle.vehicle_type.value}")
    slot.occupied_by = plate
    ticket = Ticket(
        ticket_id=str(uuid.uuid4()),
        plate=plate,
        slot_id=slot.slot_id,
        entry_time=now,
        vehicle_type=vehicle.vehicle_type,
    )
    tickets[ticket.ticket_id] = ticket
    return ticket


def vehicle_exit(lot: ParkingLot, ticket_id: str, now: datetime, tickets: dict) -> Ticket:
    """Let a vehicle leave and release its slot (SPMS-F-009).

    If the ticket is unpaid, the fee up to `now` is calculated and stored in
    ticket.amount_due; a fee above zero raises UnpaidTicketError (pay, then retry).
    Stays within the 15-minute grace period exit with no payment.
    Raises ParkingError for an unknown or already-closed ticket.
    """
    ticket = tickets.get(ticket_id)
    if ticket is None:
        raise ParkingError(f"Unknown ticket {ticket_id!r}")
    if ticket.exit_time is not None:
        raise ParkingError("Ticket is already closed")
    if not ticket.paid:
        if ticket.vehicle_type is not None:
            ticket.amount_due = calculate_fee(ticket.vehicle_type, ticket.entry_time, now)
        if ticket.amount_due > 0:
            raise UnpaidTicketError(f"Please pay Rs {ticket.amount_due:.0f} before exit")
    ticket.exit_time = now
    slot = lot.get_slot(ticket.slot_id)
    if slot.occupied_by == ticket.plate:
        slot.occupied_by = None
    return ticket
