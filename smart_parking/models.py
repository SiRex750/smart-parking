"""Core data model shared by every feature module.

Keep this file small and stable: every teammate's feature depends on it,
so changes here should go through their own PR.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    SUV = "suv"


class SlotType(Enum):
    TWO_WHEELER = "two_wheeler"
    COMPACT = "compact"
    LARGE = "large"


# Which slot types can physically hold which vehicle type.
COMPATIBLE_SLOTS = {
    VehicleType.BIKE: [SlotType.TWO_WHEELER],
    VehicleType.CAR: [SlotType.COMPACT, SlotType.LARGE],
    VehicleType.SUV: [SlotType.LARGE],
}


@dataclass
class Vehicle:
    plate: str
    vehicle_type: VehicleType
    is_ev: bool = False


@dataclass
class Slot:
    slot_id: str
    slot_type: SlotType
    level: int = 0
    is_ev: bool = False
    occupied_by: Optional[str] = None  # plate of parked vehicle
    reserved_for: Optional[str] = None  # reservation id holding this slot

    @property
    def is_free(self) -> bool:
        return self.occupied_by is None and self.reserved_for is None


@dataclass
class Ticket:
    ticket_id: str
    plate: str
    slot_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    amount_due: float = 0.0
    paid: bool = False
    vehicle_type: Optional[VehicleType] = None  # set at entry; needed for the exit fee


@dataclass
class ParkingLot:
    name: str
    slots: list = field(default_factory=list)

    def get_slot(self, slot_id: str) -> Slot:
        for slot in self.slots:
            if slot.slot_id == slot_id:
                return slot
        raise KeyError(f"No slot with id {slot_id}")

    def free_slots(self):
        return [s for s in self.slots if s.is_free]

    def occupancy(self) -> dict:
        """Real-time occupancy summary (baseline FR: SPMS-F-001)."""
        total = len(self.slots)
        occupied = sum(1 for s in self.slots if s.occupied_by is not None)
        reserved = sum(
            1 for s in self.slots if s.reserved_for is not None and s.occupied_by is None
        )
        return {
            "total": total,
            "occupied": occupied,
            "reserved": reserved,
            "available": total - occupied - reserved,
        }
