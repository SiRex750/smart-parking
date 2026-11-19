"""REST API tests (TC-API-01..06): every endpoint and every error mapping."""
from datetime import datetime

import pytest

from smart_parking.api import create_app
from smart_parking.billing import MockGateway

T0 = datetime(2026, 11, 20, 9, 0)
CAR = {"plate": "KA01AB1234", "vehicle_type": "car"}


@pytest.fixture
def client():
    return create_app(base_clock=lambda: T0).test_client()


def enter(c, **kw):
    return c.post("/api/entries", json={**CAR, **kw})


def advance(c, minutes):
    return c.post("/api/clock", json={"advance_minutes": minutes})


# --- TC-API-01 state and report -------------------------------------------------
def test_tc_api_01_state_lists_lot(client):
    s = client.get("/api/state").get_json()
    assert s["lot"] == "PES Campus Lot" and s["now"] == "2026-11-20T09:00:00"
    assert s["occupancy"]["available"] == 10 and len(s["slots"]) == 10
    assert s["slots"][0] == {"slot_id": "L0-C1", "slot_type": "compact", "level": 0,
                             "is_ev": False, "status": "free", "occupied_by": None}
    assert s["tickets"] == [] and s["reservations"] == []


def test_tc_api_01_report_by_level(client):
    enter(client)
    r = client.get("/api/report").get_json()
    assert r["0"]["compact"] == {"total": 3, "occupied": 1, "reserved": 0, "available": 2}
    assert set(r) == {"0", "1"}


# --- TC-API-02 entry ----------------------------------------------------------------
def test_tc_api_02_entry_creates_ticket(client):
    r = enter(client, plate="ka01ab1234")
    assert r.status_code == 201
    t = r.get_json()
    assert t["plate"] == "KA01AB1234" and t["slot_id"] == "L0-C1" and t["vehicle_type"] == "car"
    slots = client.get("/api/state").get_json()["slots"]
    assert slots[0]["status"] == "occupied" and slots[0]["occupied_by"] == "KA01AB1234"


@pytest.mark.parametrize("payload, status, msg", [
    ({"plate": "BAD", "vehicle_type": "car"}, 400, "Invalid number plate"),
    ({"plate": "KA01AB1234", "vehicle_type": "truck"}, 400, "vehicle_type"),
    ({"plate": "KA01AB1234"}, 400, "vehicle_type"),
])
def test_tc_api_02_entry_rejects_bad_input(client, payload, status, msg):
    r = client.post("/api/entries", json=payload)
    assert r.status_code == status and msg in r.get_json()["error"]


def test_tc_api_02_non_json_body_rejected(client):
    r = client.post("/api/entries", data="hello", content_type="text/plain")
    assert r.status_code == 400 and "JSON object" in r.get_json()["error"]


def test_tc_api_02_duplicate_and_lot_full_are_409(client):
    enter(client)
    assert enter(client).status_code == 409
    for plate in ("KA02CD0001", "KA02CD0002"):
        assert enter(client, plate=plate, vehicle_type="suv").status_code == 201
    r = enter(client, plate="KA02CD0003", vehicle_type="suv")
    assert r.status_code == 409 and "Lot full" in r.get_json()["error"]


# --- TC-API-03 fee, payment, exit -----------------------------------------------------
def test_tc_api_03_fee_pay_exit_flow(client):
    tid = enter(client).get_json()["ticket_id"]
    advance(client, 61)
    fee = client.get(f"/api/tickets/{tid}/fee").get_json()
    assert fee["amount_due"] == 60

    unpaid = client.post(f"/api/exits/{tid}")
    assert unpaid.status_code == 402 and "Please pay" in unpaid.get_json()["error"]

    wrong = client.post("/api/payments", json={"ticket_id": tid, "amount": 50})
    assert wrong.status_code == 400 and "mismatch" in wrong.get_json()["error"]

    paid = client.post("/api/payments", json={"ticket_id": tid, "amount": 60, "method": "upi"})
    assert paid.status_code == 201
    body = paid.get_json()
    assert body["ticket"]["paid"] and body["gateway_ref"].startswith("MOCK-")
    assert "Rs 60.00" in body["receipt"] and "upi" in body["receipt"]

    # fee of a paid ticket is not recalculated
    advance(client, 120)
    assert client.get(f"/api/tickets/{tid}/fee").get_json()["amount_due"] == 60

    out = client.post(f"/api/exits/{tid}")
    assert out.status_code == 200 and out.get_json()["exit_time"] == "2026-11-20T12:01:00"
    assert client.get("/api/state").get_json()["occupancy"]["occupied"] == 0


def test_tc_api_03_grace_exit_without_payment(client):
    tid = enter(client).get_json()["ticket_id"]
    advance(client, 10)
    assert client.post(f"/api/exits/{tid}").status_code == 200


@pytest.mark.parametrize("amount", [None, "abc"])
def test_tc_api_03_non_numeric_amount(client, amount):
    tid = enter(client).get_json()["ticket_id"]
    r = client.post("/api/payments", json={"ticket_id": tid, "amount": amount})
    assert r.status_code == 400 and "number" in r.get_json()["error"]


def test_tc_api_03_unknown_ticket_is_404(client):
    assert client.get("/api/tickets/nope/fee").status_code == 404
    assert client.post("/api/exits/nope").status_code == 404
    assert client.post("/api/payments", json={"ticket_id": "nope", "amount": 1}).status_code == 404


def test_tc_api_03_declined_payment_is_402():
    c = create_app(gateway=MockGateway(approve=False), base_clock=lambda: T0).test_client()
    tid = enter(c).get_json()["ticket_id"]
    advance(c, 61)
    c.get(f"/api/tickets/{tid}/fee")
    r = c.post("/api/payments", json={"ticket_id": tid, "amount": 60})
    assert r.status_code == 402 and "declined" in r.get_json()["error"]


# --- TC-API-04 reservations ---------------------------------------------------------
def test_tc_api_04_reserve_check_in(client):
    r = client.post("/api/reservations", json={**CAR, "minutes_from_now": 30})
    assert r.status_code == 201
    res = r.get_json()
    assert res["status"] == "ACTIVE" and res["start_time"] == "2026-11-20T09:30:00"
    assert client.get("/api/state").get_json()["occupancy"]["reserved"] == 1

    advance(client, 30)
    t = client.post(f"/api/reservations/{res['reservation_id']}/check-in")
    assert t.status_code == 201 and t.get_json()["slot_id"] == res["slot_id"]
    again = client.post(f"/api/reservations/{res['reservation_id']}/check-in")
    assert again.status_code == 409


def test_tc_api_04_cancel_and_unknown(client):
    rid = client.post("/api/reservations", json=CAR).get_json()["reservation_id"]
    r = client.delete(f"/api/reservations/{rid}")
    assert r.status_code == 200 and r.get_json()["status"] == "CANCELLED"
    assert client.delete(f"/api/reservations/{rid}").status_code == 409
    assert client.delete("/api/reservations/nope").status_code == 404


@pytest.mark.parametrize("minutes, msg", [("soon", "whole number"), (-5, "negative")])
def test_tc_api_04_bad_minutes(client, minutes, msg):
    r = client.post("/api/reservations", json={**CAR, "minutes_from_now": minutes})
    assert r.status_code == 400 and msg in r.get_json()["error"]


def test_tc_api_04_no_show_expires_when_clock_advances(client):
    rid = client.post("/api/reservations", json=CAR).get_json()["reservation_id"]
    advance(client, 16)
    res = client.get("/api/state").get_json()["reservations"]
    assert res[0]["reservation_id"] == rid and res[0]["status"] == "EXPIRED"


# --- TC-API-05 demo clock and reset ---------------------------------------------------
def test_tc_api_05_clock_advance_and_reset(client):
    assert advance(client, 90).get_json()["now"] == "2026-11-20T10:30:00"
    enter(client)
    r = client.post("/api/reset")
    assert r.get_json()["now"] == "2026-11-20T09:00:00"
    s = client.get("/api/state").get_json()
    assert s["tickets"] == [] and s["occupancy"]["available"] == 10


@pytest.mark.parametrize("minutes, msg", [("x", "whole number"), (-1, "negative")])
def test_tc_api_05_bad_clock_input(client, minutes, msg):
    r = advance(client, minutes)
    assert r.status_code == 400 and msg in r.get_json()["error"]


# --- TC-API-06 default clock ----------------------------------------------------------
def test_tc_api_06_default_clock_is_real_time():
    s = create_app().test_client().get("/api/state").get_json()
    assert abs(datetime.fromisoformat(s["now"]) - datetime.now()).total_seconds() < 5
