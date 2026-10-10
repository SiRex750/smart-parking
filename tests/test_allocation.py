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


def test_tc_alc_02_car_prefers_compact_over_large():
    from smart_parking.models import ParkingLot, Slot

    lot = ParkingLot("t", [Slot("L0-L1", SlotType.LARGE, 0), Slot("L0-C1", SlotType.COMPACT, 0)])
    assert find_slot(lot, CAR).slot_id == "L0-C1"


def test_tc_alc_02_lowest_level_first():
    from smart_parking.models import ParkingLot, Slot

    lot = ParkingLot("t", [Slot("L1-C1", SlotType.COMPACT, 1), Slot("L0-C1", SlotType.COMPACT, 0)])
    assert find_slot(lot, CAR).slot_id == "L0-C1"


def test_tc_alc_02_car_uses_large_when_no_compact_free():
    lot = build_demo_lot()
    for slot in lot.slots:
        if slot.slot_type == SlotType.COMPACT:
            slot.occupied_by = "TAKEN"
    chosen = find_slot(lot, CAR)
    assert chosen.slot_type == SlotType.LARGE and chosen.level == 0


def _ev_lot():
    from smart_parking.models import ParkingLot, Slot

    return ParkingLot("ev", [
        Slot("L0-EV1", SlotType.COMPACT, 0, is_ev=True),
        Slot("L1-C1", SlotType.COMPACT, 1),
    ])


def test_tc_alc_03_non_ev_car_avoids_ev_slot():
    assert find_slot(_ev_lot(), CAR).slot_id == "L1-C1"


def test_tc_alc_03_non_ev_car_gets_ev_slot_when_last_option():
    lot = _ev_lot()
    lot.get_slot("L1-C1").occupied_by = "TAKEN"
    assert find_slot(lot, CAR).slot_id == "L0-EV1"


def test_tc_alc_03_ev_car_prefers_ev_slot():
    ev_car = Vehicle("KA01EV0001", VehicleType.CAR, is_ev=True)
    assert find_slot(_ev_lot(), ev_car).slot_id == "L0-EV1"
