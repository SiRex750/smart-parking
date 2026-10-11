"""Scripted operator-console sessions (TC-UX-01 automated part)."""
from datetime import datetime, timedelta

from smart_parking.main import Console, build_demo_lot


class Script:
    """Feeds answers to the console and records what it prints; clock is controllable."""

    def __init__(self):
        self.answers, self.out = [], []
        self.now = datetime(2026, 10, 11, 9, 0)

    def ask(self, prompt):
        answer = self.answers.pop(0)
        return answer() if callable(answer) else answer

    def say(self, text):
        self.out.append(str(text))

    def text(self):
        return "\n".join(self.out)


def make():
    s = Script()
    return s, Console(build_demo_lot(), ask=s.ask, say=s.say, clock=lambda: s.now)


def test_tc_ux_01_entry_takes_three_answers_and_shows_slot():
    s, c = make()
    s.answers = ["1", "KA01AB1234", "car", "n", "0"]
    c.run()
    assert "-> slot L0-C1 (level 0)" in s.text()
    assert len(c.tickets) == 1


def test_tc_ux_01_errors_are_readable_and_console_keeps_running():
    s, c = make()
    s.answers = ["1", "BAD", "car", "n", "9", "1", "KA01AB1234", "plane", "0"]
    c.run()
    out = s.text()
    assert "Error: Invalid number plate" in out
    assert "Please choose a number from the menu." in out
    assert "Error: Vehicle type must be bike, car or suv" in out


def test_tc_ux_01_full_visit_entry_pay_exit():
    s, c = make()
    tid = lambda: next(iter(c.tickets))

    def later():
        s.now += timedelta(minutes=61)
        return "6"

    s.answers = ["1", "KA01AB1234", "car", "n", later,
                 "2", tid,               # exit refused: unpaid
                 "3", tid, "60", "upi",  # pay Rs 60
                 "2", tid,               # exit succeeds
                 "6", "0"]
    c.run()
    out = s.text()
    assert "Error: Please pay Rs 60 before exit" in out
    assert "Amount due: Rs 60" in out and "SMART PARKING - RECEIPT" in out
    assert "Goodbye KA01AB1234" in out
    assert out.rstrip().endswith("Bye.")
    assert "available 10" in out


def test_tc_ux_01_reserve_cancel_and_report():
    s, c = make()
    rid = lambda: next(iter(c.reservations))
    s.answers = ["4", "KA01AB1234", "suv", "n", "30", "7", "5", rid, "0"]
    c.run()
    out = s.text()
    assert "holds slot L0-L1 from 09:30" in out
    assert "Level 0 large        free 0/1" in out
    assert "Reservation cancelled; slot L0-L1 released." in out


def test_tc_ux_01_no_show_expired_automatically():
    s, c = make()

    def much_later():
        s.now += timedelta(minutes=20)
        return "6"

    s.answers = ["4", "KA01AB1234", "car", "n", "0", much_later, "0"]
    c.run()
    assert next(iter(c.reservations.values())).status == "EXPIRED"
