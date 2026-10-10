from datetime import datetime, timedelta

import pytest

from smart_parking.billing import calculate_fee
from smart_parking.models import VehicleType

T0 = datetime(2026, 10, 10, 9, 0)


def fee(vtype, **delta):
    return calculate_fee(vtype, T0, T0 + timedelta(**delta))


@pytest.mark.parametrize(
    "vtype, delta, expected",
    [
        (VehicleType.CAR, {"minutes": 10}, 0),
        (VehicleType.CAR, {"minutes": 15}, 0),
        (VehicleType.CAR, {"minutes": 16}, 30),
        (VehicleType.CAR, {"minutes": 61}, 60),
        (VehicleType.CAR, {"hours": 10}, 240),
        (VehicleType.BIKE, {"hours": 2}, 20),
        (VehicleType.SUV, {"hours": 3}, 120),
        (VehicleType.CAR, {"hours": 24}, 240),
        (VehicleType.CAR, {"hours": 26}, 300),
    ],
)
def test_tc_bil_01_fee_rules(vtype, delta, expected):
    assert fee(vtype, **delta) == expected


def test_tc_bil_01_exit_before_entry_rejected():
    with pytest.raises(ValueError):
        calculate_fee(VehicleType.CAR, T0, T0 - timedelta(minutes=1))


# --- SPMS-F-015 payment ----------------------------------------------------------
from smart_parking.billing import MockGateway, pay
from smart_parking.errors import PaymentError
from smart_parking.models import Ticket


def make_ticket(due=60.0):
    return Ticket("T1", "KA01AB1234", "L0-C1", T0, amount_due=due)


def test_tc_pay_01_exact_amount_marks_paid():
    t, gw = make_ticket(), MockGateway()
    p = pay(t, 60, gw, method="upi", now=T0)
    assert t.paid and p.amount == 60 and p.ticket_id == "T1"
    assert p.gateway_ref.startswith("MOCK-") and gw.charges == [(60, "upi")]


def test_tc_pay_01_wrong_amount_rejected_and_not_charged():
    t, gw = make_ticket(), MockGateway()
    with pytest.raises(PaymentError, match="mismatch"):
        pay(t, 50, gw)
    assert not t.paid and gw.charges == []


def test_tc_pay_01_declined_gateway_leaves_ticket_unpaid():
    t = make_ticket()
    with pytest.raises(PaymentError, match="declined"):
        pay(t, 60, MockGateway(approve=False))
    assert not t.paid


def test_tc_pay_01_cannot_pay_twice_or_pay_zero():
    t, gw = make_ticket(), MockGateway()
    pay(t, 60, gw)
    with pytest.raises(PaymentError, match="already"):
        pay(t, 60, gw)
    with pytest.raises(PaymentError, match="Nothing"):
        pay(make_ticket(due=0), 0, gw)


def test_tc_pay_01_negative_or_non_numeric_amount_rejected():
    for bad in (-60, "60", None):
        with pytest.raises(PaymentError):
            pay(make_ticket(), bad, MockGateway())
