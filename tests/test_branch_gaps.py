"""Part-3 gap-closing tests: edge cases found by the branch-coverage run.

Each test is named after the test case it extends (see Test Plan Appendix A).
They exercise defensive branches (state changed between steps, unknown ids,
bad input at the console) that the original feature tests did not reach.
"""
import io
import runpy
from datetime import datetime, timedelta

import pytest

from smart_parking import reservations
from smart_parking.entry_exit import vehicle_exit
from smart_parking.errors import ReservationError, UnpaidTicketError
from smart_parking.main import Console, build_demo_lot
from smart_parking.models import Ticket, Vehicle, VehicleType

NOW = datetime(2026, 10, 27, 9, 0)
CAR = Vehicle("KA01AB1234", VehicleType.CAR)


# --- TC-OCC-01 ---------------------------------------------------------------
def test_tc_occ_01_free_slots_lists_only_unoccupied_unreserved():
    lot = build_demo_lot()
    lot.slots[0].occupied_by = "KA01AB1234"
    lot.slots[1].reserved_for = "R1"
    free = lot.free_slots()
    assert len(free) == len(lot.slots) - 2
    assert lot.slots[0] not in free and lot.slots[1] not in free


# --- TC-EXT-01 ---------------------------------------------------------------
def _ticket(lot, **kw):
    base = dict(ticket_id="T1", plate="KA01AB1234", slot_id=lot.slots[0].slot_id,
                entry_time=NOW - timedelta(hours=2))
    base.update(kw)
    return Ticket(**base)


def test_tc_ext_01_ticket_without_vehicle_type_uses_stored_amount_due():
    lot = build_demo_lot()
    ticket = _ticket(lot, amount_due=60.0, vehicle_type=None)
    with pytest.raises(UnpaidTicketError):
        vehicle_exit(lot, "T1", NOW, {"T1": ticket})
    assert ticket.exit_time is None


def test_tc_ext_01_exit_does_not_free_a_slot_taken_by_another_plate():
    lot = build_demo_lot()
    slot = lot.slots[0]
    slot.occupied_by = "MH12XY0001"
    ticket = _ticket(lot, paid=True, amount_due=60.0, vehicle_type=VehicleType.CAR)
    vehicle_exit(lot, "T1", NOW, {"T1": ticket})
    assert ticket.exit_time == NOW
    assert slot.occupied_by == "MH12XY0001"


# --- TC-RES-02 / 03 / 04: slot hold already released elsewhere -----------------
def _reserved(lot, store):
    r = reservations.create(lot, CAR, NOW, store)
    lot.get_slot(r.slot_id).reserved_for = "OTHER-RES"  # slot re-assigned meanwhile
    return r


def test_tc_res_02_cancel_leaves_a_slot_held_by_another_reservation():
    lot, store = build_demo_lot(), {}
    r = _reserved(lot, store)
    reservations.cancel(lot, r.reservation_id, store)
    assert r.status == reservations.CANCELLED
    assert lot.get_slot(r.slot_id).reserved_for == "OTHER-RES"


def test_tc_res_03_expiry_leaves_a_slot_held_by_another_reservation():
    lot, store = build_demo_lot(), {}
    r = _reserved(lot, store)
    assert reservations.expire_no_shows(lot, NOW + timedelta(minutes=16), store) == 1
    assert r.status == reservations.EXPIRED
    assert lot.get_slot(r.slot_id).reserved_for == "OTHER-RES"


def test_tc_res_04_late_check_in_leaves_a_slot_held_by_another_reservation():
    lot, store = build_demo_lot(), {}
    r = _reserved(lot, store)
    with pytest.raises(ReservationError):
        reservations.check_in(lot, r.reservation_id, NOW + timedelta(minutes=16), store, {})
    assert r.status == reservations.EXPIRED
    assert lot.get_slot(r.slot_id).reserved_for == "OTHER-RES"


# --- TC-UX-01: console input errors and entry point ----------------------------
class Script:
    def __init__(self, answers):
        self.answers, self.out = list(answers), []

    def ask(self, prompt):
        answer = self.answers.pop(0)
        return answer() if callable(answer) else answer

    def say(self, text):
        self.out.append(str(text))


def _console(answers):
    s = Script(answers)
    return s, Console(build_demo_lot(), ask=s.ask, say=s.say, clock=lambda: NOW)


def test_tc_ux_01_pay_unknown_ticket_is_a_readable_error():
    s, c = _console(["3", "NO-SUCH-TICKET", "0"])
    c.run()
    assert any(line.startswith("Error: Unknown ticket") for line in s.out)


def test_tc_ux_01_pay_non_numeric_amount_is_a_readable_error():
    s, c = _console(["1", "KA01AB1234", "car", "n",
                     "3", lambda: next(iter(c.tickets)), "abc", "0"])
    c.run()
    assert "Error: Amount must be a number" in s.out
    assert not next(iter(c.tickets.values())).paid


def test_tc_ux_01_main_starts_console_and_exits_on_zero(monkeypatch, capsys):
    from smart_parking.main import main
    # Console binds the real input() at import time, so feed it through stdin.
    monkeypatch.setattr("sys.stdin", io.StringIO("0\n"))
    main()
    assert "Bye." in capsys.readouterr().out


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_tc_ux_01_module_entry_point_runs(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("0\n"))
    runpy.run_module("smart_parking.main", run_name="__main__")
    assert "Bye." in capsys.readouterr().out
