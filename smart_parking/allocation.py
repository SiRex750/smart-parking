"""Slot allocation (SPMS-F-002..005)."""
from typing import Optional

from smart_parking.errors import LotFullError
from smart_parking.models import COMPATIBLE_SLOTS, ParkingLot, Slot, Vehicle


def find_slot(lot: ParkingLot, vehicle: Vehicle) -> Optional[Slot]:
    """Return the best free slot that can hold the vehicle, or None if none fits.

    EV priority (SPMS-F-004): EV-charging slots go to non-EV vehicles only when no
    other suitable slot is free, and EV vehicles are offered EV slots first.
    Best fit (SPMS-F-003): then the smallest suitable slot type (COMPATIBLE_SLOTS
    lists types smallest-first), then the lowest level, then slot order in the lot.
    Does not change any slot's state; the caller occupies or reserves it.
    """
    allowed = COMPATIBLE_SLOTS[vehicle.vehicle_type]
    candidates = [s for s in lot.slots if s.is_free and s.slot_type in allowed]
    if not candidates:
        return None
    return min(candidates, key=lambda s: (s.is_ev != vehicle.is_ev, allowed.index(s.slot_type), s.level))


def require_slot(lot: ParkingLot, vehicle: Vehicle) -> Slot:
    """Like find_slot, but raise a clear LotFullError when nothing fits (SPMS-F-005).

    The message names the vehicle type and how many compatible slots exist, e.g.
    "Lot full for suv: all 2 large slot(s) are occupied or reserved".
    """
    slot = find_slot(lot, vehicle)
    if slot is not None:
        return slot
    allowed = COMPATIBLE_SLOTS[vehicle.vehicle_type]
    total = sum(1 for s in lot.slots if s.slot_type in allowed)
    kinds = "/".join(t.value for t in allowed)
    if total == 0:
        raise LotFullError(f"Lot full for {vehicle.vehicle_type.value}: this lot has no {kinds} slots")
    raise LotFullError(
        f"Lot full for {vehicle.vehicle_type.value}: all {total} {kinds} slot(s) are occupied or reserved"
    )
