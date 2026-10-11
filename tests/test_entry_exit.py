import pytest

from smart_parking.entry_exit import validate_plate


@pytest.mark.parametrize("plate", ["KA01AB1234", "MH12XY0001", "DL3C1234", "KA05MN4321"])
def test_tc_ent_01_valid_plates(plate):
    assert validate_plate(plate)


def test_tc_ent_01_lowercase_and_spaces_are_normalised():
    assert validate_plate("  ka01ab1234 ")


@pytest.mark.parametrize(
    "plate",
    ["", "1234", "KA-01-AB-1234", "KA01AB12345", "KA01 AB 1234", "KA01'; DROP", None, 1234],
)
def test_tc_ent_01_invalid_plates(plate):
    assert not validate_plate(plate)


# --- SPMS-F-007 vehicle entry -------------------------------------------------
import uuid
from datetime import datetime

from smart_parking.entry_exit import vehicle_entry
from smart_parking.errors import InvalidPlateError, LotFullError
from smart_parking.main import build_demo_lot
from smart_parking.models import Vehicle, VehicleType

NOW = datetime(2026, 10, 10, 9, 0)


def test_tc_ent_02_entry_issues_ticket_and_occupies_slot():
    lot, tickets = build_demo_lot(), {}
    ticket = vehicle_entry(lot, Vehicle("ka01ab1234", VehicleType.CAR), NOW, tickets)
    assert tickets[ticket.ticket_id] is ticket
    assert ticket.plate == "KA01AB1234"
    assert ticket.entry_time == NOW and not ticket.paid
    assert lot.get_slot(ticket.slot_id).occupied_by == "KA01AB1234"
    assert lot.occupancy()["occupied"] == 1
    assert uuid.UUID(ticket.ticket_id).version == 4


def test_tc_ent_02_invalid_plate_rejected_without_changes():
    lot, tickets = build_demo_lot(), {}
    with pytest.raises(InvalidPlateError):
        vehicle_entry(lot, Vehicle("BAD", VehicleType.CAR), NOW, tickets)
    assert tickets == {} and lot.occupancy()["occupied"] == 0


def test_tc_ent_02_lot_full_raises():
    lot, tickets = build_demo_lot(), {}
    vehicle_entry(lot, Vehicle("KA01AB0001", VehicleType.SUV), NOW, tickets)
    vehicle_entry(lot, Vehicle("KA01AB0002", VehicleType.SUV), NOW, tickets)
    with pytest.raises(LotFullError):
        vehicle_entry(lot, Vehicle("KA01AB0003", VehicleType.SUV), NOW, tickets)
    assert len(tickets) == 2


# --- SPMS-F-008 duplicate entry -----------------------------------------------
from smart_parking.errors import DuplicateEntryError


def test_tc_ent_03_same_plate_twice_rejected():
    lot, tickets = build_demo_lot(), {}
    vehicle_entry(lot, Vehicle("KA01AB1234", VehicleType.CAR), NOW, tickets)
    with pytest.raises(DuplicateEntryError):
        vehicle_entry(lot, Vehicle("KA01AB1234", VehicleType.CAR), NOW, tickets)
    assert len(tickets) == 1 and lot.occupancy()["occupied"] == 1


def test_tc_ent_03_duplicate_check_ignores_case_and_spaces():
    lot, tickets = build_demo_lot(), {}
    vehicle_entry(lot, Vehicle("KA01AB1234", VehicleType.CAR), NOW, tickets)
    with pytest.raises(DuplicateEntryError):
        vehicle_entry(lot, Vehicle(" ka01ab1234 ", VehicleType.CAR), NOW, tickets)


def test_tc_ent_03_different_plates_both_allowed():
    lot, tickets = build_demo_lot(), {}
    vehicle_entry(lot, Vehicle("KA01AB1234", VehicleType.CAR), NOW, tickets)
    vehicle_entry(lot, Vehicle("KA01AB1235", VehicleType.CAR), NOW, tickets)
    assert lot.occupancy()["occupied"] == 2


# --- SPMS-F-009 vehicle exit ------------------------------------------------------
from datetime import timedelta

from smart_parking.billing import MockGateway, pay
from smart_parking.entry_exit import vehicle_exit
from smart_parking.errors import ParkingError, UnpaidTicketError


def _parked(minutes):
    lot, tickets = build_demo_lot(), {}
    t = vehicle_entry(lot, Vehicle("KA01AB1234", VehicleType.CAR), NOW, tickets)
    return lot, tickets, t, NOW + timedelta(minutes=minutes)


def test_tc_ext_01_unpaid_exit_refused_and_amount_set():
    lot, tickets, t, later = _parked(120)
    with pytest.raises(UnpaidTicketError, match="60"):
        vehicle_exit(lot, t.ticket_id, later, tickets)
    assert t.amount_due == 60 and t.exit_time is None
    assert lot.get_slot(t.slot_id).occupied_by == "KA01AB1234"


def test_tc_ext_01_paid_exit_releases_slot():
    lot, tickets, t, later = _parked(120)
    with pytest.raises(UnpaidTicketError):
        vehicle_exit(lot, t.ticket_id, later, tickets)
    pay(t, t.amount_due, MockGateway())
    out = vehicle_exit(lot, t.ticket_id, later, tickets)
    assert out.exit_time == later
    assert lot.get_slot(t.slot_id).is_free and lot.occupancy()["occupied"] == 0


def test_tc_ext_01_grace_period_exit_needs_no_payment():
    lot, tickets, t, later = _parked(10)
    vehicle_exit(lot, t.ticket_id, later, tickets)
    assert t.amount_due == 0 and lot.get_slot(t.slot_id).is_free


def test_tc_ext_01_unknown_or_closed_ticket_rejected():
    lot, tickets, t, later = _parked(10)
    with pytest.raises(ParkingError, match="Unknown"):
        vehicle_exit(lot, "nope", later, tickets)
    vehicle_exit(lot, t.ticket_id, later, tickets)
    with pytest.raises(ParkingError, match="closed"):
        vehicle_exit(lot, t.ticket_id, later, tickets)


def test_tc_ent_02_ticket_records_vehicle_type():
    _, _, t, _ = _parked(0)
    assert t.vehicle_type == VehicleType.CAR
