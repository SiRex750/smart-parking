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
