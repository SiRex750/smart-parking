from smart_parking.allocation import find_slot
from smart_parking.main import build_demo_lot
from smart_parking.models import SlotType, Vehicle, VehicleType

BIKE = Vehicle("KA01AB0001", VehicleType.BIKE)
CAR = Vehicle("KA01AB0002", VehicleType.CAR)
SUV = Vehicle("KA01AB0003", VehicleType.SUV)


def test_tc_alc_01_bike_gets_two_wheeler_slot():
    assert find_slot(build_demo_lot(), BIKE).slot_type == SlotType.TWO_WHEELER


def test_tc_alc_01_car_gets_compact_or_large():
    assert find_slot(build_demo_lot(), CAR).slot_type in (SlotType.COMPACT, SlotType.LARGE)


def test_tc_alc_01_suv_only_gets_large():
    lot = build_demo_lot()
    assert find_slot(lot, SUV).slot_type == SlotType.LARGE
    for slot in lot.slots:
        if slot.slot_type == SlotType.LARGE:
            slot.occupied_by = "TAKEN"
    assert find_slot(lot, SUV) is None


def test_tc_alc_01_skips_reserved_and_occupied_slots():
    lot = build_demo_lot()
    for slot in lot.slots:
        if slot.slot_type == SlotType.TWO_WHEELER:
            slot.reserved_for = "R1"
    assert find_slot(lot, BIKE) is None


def test_tc_alc_01_does_not_change_lot_state():
    lot = build_demo_lot()
    before = lot.occupancy()
    find_slot(lot, CAR)
    assert lot.occupancy() == before
