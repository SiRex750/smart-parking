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


# --- SPMS-F-011 cancel ----------------------------------------------------------
from smart_parking.errors import ReservationError
from smart_parking.reservations import CANCELLED, cancel


def test_tc_res_02_cancel_releases_slot():
    lot, res = build_demo_lot(), {}
    r = create(lot, CAR, START, res)
    out = cancel(lot, r.reservation_id, res)
    assert out.status == CANCELLED
    assert lot.get_slot(r.slot_id).is_free
    assert lot.occupancy()["reserved"] == 0


def test_tc_res_02_cancel_twice_rejected():
    lot, res = build_demo_lot(), {}
    r = create(lot, CAR, START, res)
    cancel(lot, r.reservation_id, res)
    with pytest.raises(ReservationError):
        cancel(lot, r.reservation_id, res)


def test_tc_res_02_unknown_id_rejected():
    with pytest.raises(ReservationError):
        cancel(build_demo_lot(), "does-not-exist", {})


def test_tc_res_02_released_slot_can_be_reserved_again():
    lot, res = build_demo_lot(), {}
    r = create(lot, CAR, START, res)
    cancel(lot, r.reservation_id, res)
    assert create(lot, CAR, START, res).slot_id == r.slot_id


# --- SPMS-F-012 no-show expiry ----------------------------------------------------
from datetime import timedelta

from smart_parking.reservations import EXPIRED, expire_no_shows


@pytest.mark.parametrize("minutes, expected_status, expired_count", [
    (14, ACTIVE, 0), (15, ACTIVE, 0), (16, EXPIRED, 1),
])
def test_tc_res_03_expiry_boundary(minutes, expected_status, expired_count):
    lot, res = build_demo_lot(), {}
    r = create(lot, CAR, START, res)
    assert expire_no_shows(lot, START + timedelta(minutes=minutes), res) == expired_count
    assert r.status == expected_status
    assert lot.get_slot(r.slot_id).is_free == (expected_status == EXPIRED)


def test_tc_res_03_only_active_reservations_expire():
    lot, res = build_demo_lot(), {}
    a = create(lot, CAR, START, res)
    b = create(lot, Vehicle("KA01AB9999", VehicleType.CAR), START, res)
    cancel(lot, a.reservation_id, res)
    assert expire_no_shows(lot, START + timedelta(hours=1), res) == 1
    assert a.status == CANCELLED and b.status == EXPIRED


def test_tc_res_03_future_reservations_untouched():
    lot, res = build_demo_lot(), {}
    r = create(lot, CAR, START + timedelta(hours=2), res)
    assert expire_no_shows(lot, START, res) == 0 and r.status == ACTIVE


# --- SPMS-F-013 check-in ----------------------------------------------------------
from smart_parking.errors import DuplicateEntryError
from smart_parking.reservations import USED, check_in


def test_tc_res_04_check_in_parks_in_held_slot():
    lot, res, tickets = build_demo_lot(), {}, {}
    r = create(lot, CAR, START, res)
    t = check_in(lot, r.reservation_id, START + timedelta(minutes=5), res, tickets)
    slot = lot.get_slot(r.slot_id)
    assert t.slot_id == r.slot_id and tickets[t.ticket_id] is t
    assert slot.occupied_by == "KA01AB1234" and slot.reserved_for is None
    assert r.status == USED and t.vehicle_type == VehicleType.CAR
    occ = lot.occupancy()
    assert occ["occupied"] == 1 and occ["reserved"] == 0


def test_tc_res_04_unknown_or_used_reservation_rejected():
    lot, res, tickets = build_demo_lot(), {}, {}
    with pytest.raises(ReservationError):
        check_in(lot, "unknown", START, res, tickets)
    r = create(lot, CAR, START, res)
    check_in(lot, r.reservation_id, START, res, tickets)
    with pytest.raises(ReservationError):
        check_in(lot, r.reservation_id, START, res, tickets)


def test_tc_res_04_late_check_in_expires_reservation():
    lot, res, tickets = build_demo_lot(), {}, {}
    r = create(lot, CAR, START, res)
    with pytest.raises(ReservationError, match="expired"):
        check_in(lot, r.reservation_id, START + timedelta(minutes=16), res, tickets)
    assert r.status == EXPIRED and lot.get_slot(r.slot_id).is_free and tickets == {}


def test_tc_res_04_plate_already_parked_rejected():
    lot, res, tickets = build_demo_lot(), {}, {}
    r = create(lot, CAR, START, res)
    lot.get_slot("L1-C1").occupied_by = "KA01AB1234"
    with pytest.raises(DuplicateEntryError):
        check_in(lot, r.reservation_id, START, res, tickets)
    assert r.status == ACTIVE
