"""Small demo entry point: `python -m smart_parking.main`.

Extend this as features land so the demo shows the whole system.
"""
from smart_parking.models import ParkingLot, Slot, SlotType


def build_demo_lot() -> ParkingLot:
    slots = []
    for level in range(2):
        for i in range(1, 4):
            slots.append(Slot(f"L{level}-C{i}", SlotType.COMPACT, level))
        slots.append(Slot(f"L{level}-L1", SlotType.LARGE, level))
        slots.append(Slot(f"L{level}-B1", SlotType.TWO_WHEELER, level))
    return ParkingLot("PES Campus Lot", slots)


def main():
    lot = build_demo_lot()
    print("Smart Parking Management System")
    print("Lot:", lot.name)
    print("Occupancy:", lot.occupancy())


if __name__ == "__main__":
    main()
