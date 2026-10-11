"""End-to-end flows across modules (Test Plan TC-INT-01)."""
from datetime import datetime, timedelta

import pytest

from smart_parking.billing import MockGateway, calculate_fee, pay, receipt
from smart_parking.entry_exit import vehicle_entry, vehicle_exit
from smart_parking.errors import UnpaidTicketError
from smart_parking.main import build_demo_lot
from smart_parking.models import Vehicle, VehicleType

T0 = datetime(2026, 10, 11, 9, 0)


def test_tc_int_01_entry_pay_exit():
    lot, tickets = build_demo_lot(), {}
    t = vehicle_entry(lot, Vehicle("KA01AB1234", VehicleType.CAR), T0, tickets)
    later = T0 + timedelta(minutes=61)

    with pytest.raises(UnpaidTicketError):
        vehicle_exit(lot, t.ticket_id, later, tickets)
    assert t.amount_due == calculate_fee(VehicleType.CAR, T0, later) == 60

    payment = pay(t, 60, MockGateway(), method="upi", now=later)
    vehicle_exit(lot, t.ticket_id, later, tickets)

    assert t.paid and t.exit_time == later
    assert "Rs 60.00" in receipt(t, payment)
    assert lot.occupancy() == {"total": 10, "occupied": 0, "reserved": 0, "available": 10}


def test_tc_int_01_many_vehicles_fill_and_empty_lot():
    lot, tickets = build_demo_lot(), {}
    plates = [f"KA01AB{i:04d}" for i in range(6)]
    for p in plates:
        vehicle_entry(lot, Vehicle(p, VehicleType.CAR), T0, tickets)
    assert lot.occupancy()["occupied"] == 6
    for t in list(tickets.values()):
        vehicle_exit(lot, t.ticket_id, T0 + timedelta(minutes=10), tickets)
    assert lot.occupancy()["available"] == 10


# --- TC-INT-02 reserve -> check-in -> exit --------------------------------------
from smart_parking.reservations import USED, check_in, create


def test_tc_int_02_reserve_check_in_exit_within_grace():
    lot, res, tickets = build_demo_lot(), {}, {}
    r = create(lot, Vehicle("KA01AB1234", VehicleType.SUV), T0, res)
    t = check_in(lot, r.reservation_id, T0 + timedelta(minutes=5), res, tickets)
    assert t.slot_id == r.slot_id and r.status == USED
    vehicle_exit(lot, t.ticket_id, T0 + timedelta(minutes=15), tickets)
    assert t.amount_due == 0
    assert lot.occupancy()["available"] == 10
