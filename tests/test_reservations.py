import uuid
from datetime import datetime

import pytest

from smart_parking.errors import LotFullError
from smart_parking.main import build_demo_lot
from smart_parking.models import SlotType, Vehicle, VehicleType
from smart_parking.reservations import ACTIVE, create

START = datetime(2026, 10, 10, 10, 0)
CAR = Vehicle("KA01AB1234", VehicleType.CAR)


def test_tc_res_01_reservation_holds_compatible_slot():
    lot, res = build_demo_lot(), {}
    r = create(lot, CAR, START, res)
    slot = lot.get_slot(r.slot_id)
    assert slot.reserved_for == r.reservation_id
    assert slot.slot_type in (SlotType.COMPACT, SlotType.LARGE)
    assert r.status == ACTIVE and res[r.reservation_id] is r


def test_tc_res_01_occupancy_shows_reserved():
    lot = build_demo_lot()
    create(lot, CAR, START, {})
    occ = lot.occupancy()
    assert occ["reserved"] == 1 and occ["available"] == 9


def test_tc_res_01_id_is_uuid4():
    r = create(build_demo_lot(), CAR, START, {})
    assert uuid.UUID(r.reservation_id).version == 4


def test_tc_res_01_two_reservations_get_different_slots():
    lot, res = build_demo_lot(), {}
    a = create(lot, CAR, START, res)
    b = create(lot, Vehicle("KA01AB9999", VehicleType.CAR), START, res)
    assert a.slot_id != b.slot_id


def test_tc_res_01_full_lot_raises():
    lot, res = build_demo_lot(), {}
    create(lot, Vehicle("KA01AB0001", VehicleType.SUV), START, res)
    create(lot, Vehicle("KA01AB0002", VehicleType.SUV), START, res)
    with pytest.raises(LotFullError):
        create(lot, Vehicle("KA01AB0003", VehicleType.SUV), START, res)
    assert len(res) == 2
