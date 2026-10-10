"""Slot allocation (SPMS-F-002..005)."""
from typing import Optional

from smart_parking.models import COMPATIBLE_SLOTS, ParkingLot, Slot, Vehicle


def find_slot(lot: ParkingLot, vehicle: Vehicle) -> Optional[Slot]:
    """Return a free slot that can hold the vehicle, or None if none fits.

    Does not change any slot's state; the caller occupies or reserves it.
    """
    allowed = COMPATIBLE_SLOTS[vehicle.vehicle_type]
    for slot in lot.slots:
        if slot.is_free and slot.slot_type in allowed:
            return slot
    return None
