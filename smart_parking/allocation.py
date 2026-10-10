"""Slot allocation (SPMS-F-002..005)."""
from typing import Optional

from smart_parking.models import COMPATIBLE_SLOTS, ParkingLot, Slot, Vehicle


def find_slot(lot: ParkingLot, vehicle: Vehicle) -> Optional[Slot]:
    """Return the best free slot that can hold the vehicle, or None if none fits.

    Best fit (SPMS-F-003): the smallest suitable slot type first (COMPATIBLE_SLOTS
    lists types smallest-first), then the lowest level, then slot order in the lot.
    Does not change any slot's state; the caller occupies or reserves it.
    """
    allowed = COMPATIBLE_SLOTS[vehicle.vehicle_type]
    candidates = [s for s in lot.slots if s.is_free and s.slot_type in allowed]
    if not candidates:
        return None
    return min(candidates, key=lambda s: (allowed.index(s.slot_type), s.level))
