"""Vehicle entry and exit (SPMS-F-006..009)."""
import re
import uuid
from datetime import datetime

from smart_parking.allocation import find_slot
from smart_parking.errors import InvalidPlateError, LotFullError
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
    Raises InvalidPlateError or LotFullError; the lot is unchanged on error.
    """
    if not validate_plate(vehicle.plate):
        raise InvalidPlateError(f"Invalid number plate: {vehicle.plate!r}")
    plate = vehicle.plate.strip().upper()
    slot = find_slot(lot, vehicle)
    if slot is None:
        raise LotFullError(f"Lot full for {vehicle.vehicle_type.value}")
    slot.occupied_by = plate
    ticket = Ticket(ticket_id=str(uuid.uuid4()), plate=plate, slot_id=slot.slot_id, entry_time=now)
    tickets[ticket.ticket_id] = ticket
    return ticket
