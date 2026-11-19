"""REST API for the web UI (SAD §4.3): `python -m smart_parking.api`.

A thin Flask layer over the existing service modules. It holds no business logic:
each route parses JSON, calls a service function and maps ParkingError subclasses
to HTTP status codes. State is in memory (SAD ADR-003), one lot per app instance.
A demo clock offset lets the UI simulate time passing so fees and expiry can be shown.
"""
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

from smart_parking import billing, entry_exit, reports, reservations
from smart_parking.errors import (
    DuplicateEntryError,
    InvalidPlateError,
    LotFullError,
    ParkingError,
    PaymentError,
    ReservationError,
    UnpaidTicketError,
)
from smart_parking.main import build_demo_lot
from smart_parking.models import Vehicle, VehicleType

TYPES = {t.value: t for t in VehicleType}

STATUS = {
    InvalidPlateError: 400,
    PaymentError: 400,
    UnpaidTicketError: 402,
    DuplicateEntryError: 409,
    LotFullError: 409,
    ReservationError: 409,
}


class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _iso(dt):
    return dt.isoformat(timespec="seconds") if dt else None


def _ticket(t):
    return {
        "ticket_id": t.ticket_id, "plate": t.plate, "slot_id": t.slot_id,
        "vehicle_type": t.vehicle_type.value if t.vehicle_type else None,
        "entry_time": _iso(t.entry_time), "exit_time": _iso(t.exit_time),
        "amount_due": t.amount_due, "paid": t.paid,
    }


def _reservation(r):
    return {
        "reservation_id": r.reservation_id, "plate": r.plate, "vehicle_type": r.vehicle_type.value,
        "slot_id": r.slot_id, "start_time": _iso(r.start_time), "status": r.status,
    }


def _slot(s):
    status = "occupied" if s.occupied_by else "reserved" if s.reserved_for else "free"
    return {
        "slot_id": s.slot_id, "slot_type": s.slot_type.value, "level": s.level, "is_ev": s.is_ev,
        "status": status, "occupied_by": s.occupied_by,
    }


def create_app(lot=None, gateway=None, base_clock=datetime.now):
    app = Flask(__name__)
    state = {"offset": timedelta(0)}

    def reset(new_lot=None):
        state.update(lot=new_lot or build_demo_lot(), tickets={}, reservations={}, payments={},
                     gateway=gateway or billing.MockGateway(), offset=timedelta(0))

    reset(lot)

    def now():
        return base_clock() + state["offset"]

    def body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ApiError("Request body must be a JSON object")
        return data

    def vehicle(data):
        vtype = TYPES.get(str(data.get("vehicle_type", "")).lower())
        if vtype is None:
            raise ApiError("vehicle_type must be bike, car or suv")
        return Vehicle(str(data.get("plate", "")), vtype, bool(data.get("is_ev", False)))

    def ticket_or_404(ticket_id):
        t = state["tickets"].get(ticket_id)
        if t is None:
            raise ApiError(f"Unknown ticket {ticket_id!r}", 404)
        return t

    @app.errorhandler(ApiError)
    def api_error(err):
        return jsonify(error=str(err)), err.status

    @app.errorhandler(ParkingError)
    def parking_error(err):
        status = 404 if str(err).startswith("Unknown") else STATUS.get(type(err), 400)
        if isinstance(err, PaymentError) and "declined" in str(err):
            status = 402
        return jsonify(error=str(err)), status

    @app.before_request
    def expire():
        reservations.expire_no_shows(state["lot"], now(), state["reservations"])

    @app.get("/api/state")
    def get_state():
        lot = state["lot"]
        return jsonify(
            lot=lot.name, now=_iso(now()), occupancy=lot.occupancy(),
            slots=[_slot(s) for s in lot.slots],
            tickets=[_ticket(t) for t in state["tickets"].values()],
            reservations=[_reservation(r) for r in state["reservations"].values()],
        )

    @app.get("/api/report")
    def get_report():
        return jsonify({str(level): row for level, row in reports.occupancy_by_level_and_type(state["lot"]).items()})

    @app.post("/api/entries")
    def post_entry():
        t = entry_exit.vehicle_entry(state["lot"], vehicle(body()), now(), state["tickets"])
        return jsonify(_ticket(t)), 201

    @app.get("/api/tickets/<ticket_id>/fee")
    def get_fee(ticket_id):
        t = ticket_or_404(ticket_id)
        if not t.paid:
            t.amount_due = billing.calculate_fee(t.vehicle_type, t.entry_time, now())
        return jsonify(_ticket(t))

    @app.post("/api/payments")
    def post_payment():
        data = body()
        t = ticket_or_404(str(data.get("ticket_id", "")))
        try:
            amount = float(data.get("amount"))
        except (TypeError, ValueError):
            raise ApiError("amount must be a number")
        p = billing.pay(t, amount, state["gateway"], str(data.get("method") or "cash"), now=now())
        state["payments"][t.ticket_id] = p
        return jsonify(ticket=_ticket(t), gateway_ref=p.gateway_ref, receipt=billing.receipt(t, p)), 201

    @app.post("/api/exits/<ticket_id>")
    def post_exit(ticket_id):
        ticket_or_404(ticket_id)
        t = entry_exit.vehicle_exit(state["lot"], ticket_id, now(), state["tickets"])
        return jsonify(_ticket(t))

    @app.post("/api/reservations")
    def post_reservation():
        data = body()
        try:
            minutes = int(data.get("minutes_from_now", 0))
        except (TypeError, ValueError):
            raise ApiError("minutes_from_now must be a whole number")
        if minutes < 0:
            raise ApiError("minutes_from_now cannot be negative")
        r = reservations.create(state["lot"], vehicle(data), now() + timedelta(minutes=minutes),
                                state["reservations"])
        return jsonify(_reservation(r)), 201

    @app.delete("/api/reservations/<reservation_id>")
    def delete_reservation(reservation_id):
        r = reservations.cancel(state["lot"], reservation_id, state["reservations"])
        return jsonify(_reservation(r))

    @app.post("/api/reservations/<reservation_id>/check-in")
    def post_check_in(reservation_id):
        t = reservations.check_in(state["lot"], reservation_id, now(), state["reservations"], state["tickets"])
        return jsonify(_ticket(t)), 201

    @app.post("/api/clock")
    def post_clock():
        try:
            minutes = int(body().get("advance_minutes", 0))
        except (TypeError, ValueError):
            raise ApiError("advance_minutes must be a whole number")
        if minutes < 0:
            raise ApiError("advance_minutes cannot be negative")
        state["offset"] += timedelta(minutes=minutes)
        reservations.expire_no_shows(state["lot"], now(), state["reservations"])
        return jsonify(now=_iso(now()))

    @app.post("/api/reset")
    def post_reset():
        reset()
        return jsonify(now=_iso(now()))

    return app


def main():  # pragma: no cover - starts a server
    create_app().run(host="127.0.0.1", port=5000)


if __name__ == "__main__":  # pragma: no cover
    main()
