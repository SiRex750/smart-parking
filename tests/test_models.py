import pytest

from smart_parking.main import build_demo_lot
from smart_parking.models import COMPATIBLE_SLOTS, SlotType, VehicleType


def test_demo_lot_has_ten_slots():
    lot = build_demo_lot()
    assert len(lot.slots) == 10


def test_empty_lot_is_fully_available():
    occ = build_demo_lot().occupancy()
    assert occ == {"total": 10, "occupied": 0, "reserved": 0, "available": 10}


def test_occupancy_counts_occupied_and_reserved():
    lot = build_demo_lot()
    lot.get_slot("L0-C1").occupied_by = "KA01AB1234"
    lot.get_slot("L0-C2").reserved_for = "R1"
    occ = lot.occupancy()
    assert occ["occupied"] == 1
    assert occ["reserved"] == 1
    assert occ["available"] == 8


def test_unknown_slot_raises():
    with pytest.raises(KeyError):
        build_demo_lot().get_slot("NOPE")


def test_suv_only_fits_large():
    assert COMPATIBLE_SLOTS[VehicleType.SUV] == [SlotType.LARGE]
