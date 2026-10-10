"""Reporting (SPMS-F-017)."""
from smart_parking.models import ParkingLot


def occupancy_by_level_and_type(lot: ParkingLot) -> dict:
    """Occupancy broken down by level and slot type.

    Returns {level: {slot_type_value: {"total", "occupied", "reserved", "available"}}}.
    A slot that is occupied counts as occupied even if it also has a reservation.
    """
    report: dict = {}
    for slot in lot.slots:
        row = report.setdefault(slot.level, {}).setdefault(
            slot.slot_type.value, {"total": 0, "occupied": 0, "reserved": 0, "available": 0}
        )
        row["total"] += 1
        if slot.occupied_by is not None:
            row["occupied"] += 1
        elif slot.reserved_for is not None:
            row["reserved"] += 1
        else:
            row["available"] += 1
    return report
