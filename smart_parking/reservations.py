"""Reservations (SPMS-F-010..013)."""
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from smart_parking.allocation import find_slot
from smart_parking.errors import LotFullError, ReservationError
from smart_parking.models import ParkingLot, Vehicle, VehicleType

ACTIVE, CANCELLED, EXPIRED, USED = "ACTIVE", "CANCELLED", "EXPIRED", "USED"
NO_SHOW_GRACE = timedelta(minutes=15)


@dataclass
class Reservation:
    reservation_id: str
    plate: str
    vehicle_type: VehicleType
    slot_id: str
    start_time: datetime
    status: str = ACTIVE


def create(lot: ParkingLot, vehicle: Vehicle, start: datetime, reservations: dict) -> Reservation:
    """Hold the best suitable slot for a vehicle from `start` (SPMS-F-010).

    Raises LotFullError if no suitable slot is free; the lot is unchanged then.
    """
    slot = find_slot(lot, vehicle)
    if slot is None:
        raise LotFullError(f"No {vehicle.vehicle_type.value} slot available to reserve")
    reservation = Reservation(
        reservation_id=str(uuid.uuid4()),
        plate=vehicle.plate.strip().upper(),
        vehicle_type=vehicle.vehicle_type,
        slot_id=slot.slot_id,
        start_time=start,
    )
    slot.reserved_for = reservation.reservation_id
    reservations[reservation.reservation_id] = reservation
    return reservation


def cancel(lot: ParkingLot, reservation_id: str, reservations: dict) -> Reservation:
    """Cancel an ACTIVE reservation and release its held slot (SPMS-F-011).

    Raises ReservationError if the id is unknown or the reservation is not ACTIVE.
    """
    reservation = reservations.get(reservation_id)
    if reservation is None:
        raise ReservationError(f"Unknown reservation {reservation_id!r}")
    if reservation.status != ACTIVE:
        raise ReservationError(f"Reservation is {reservation.status}, not ACTIVE")
    slot = lot.get_slot(reservation.slot_id)
    if slot.reserved_for == reservation_id:
        slot.reserved_for = None
    reservation.status = CANCELLED
    return reservation


def expire_no_shows(lot: ParkingLot, now: datetime, reservations: dict) -> int:
    """Expire ACTIVE reservations more than 15 minutes past their start (SPMS-F-012).

    Releases each expired reservation's slot and returns how many were expired.
    """
    expired = 0
    for reservation in reservations.values():
        if reservation.status == ACTIVE and now > reservation.start_time + NO_SHOW_GRACE:
            slot = lot.get_slot(reservation.slot_id)
            if slot.reserved_for == reservation.reservation_id:
                slot.reserved_for = None
            reservation.status = EXPIRED
            expired += 1
    return expired
