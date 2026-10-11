"""Operator console: `python -m smart_parking.main`.

All I/O lives here; services in the other modules never print or read input.
`Console` takes injectable ask/say/clock functions so tests can script a session.
"""
from datetime import datetime, timedelta

from smart_parking import billing, entry_exit, reports, reservations
from smart_parking.errors import ParkingError
from smart_parking.models import ParkingLot, Slot, SlotType, Vehicle, VehicleType

MENU = """
1) Vehicle entry      2) Vehicle exit       3) Pay ticket
4) Reserve a slot     5) Cancel reservation 8) Check in reservation
6) Occupancy          7) Report by level    0) Quit"""

TYPES = {"bike": VehicleType.BIKE, "car": VehicleType.CAR, "suv": VehicleType.SUV}


def build_demo_lot() -> ParkingLot:
    slots = []
    for level in range(2):
        for i in range(1, 4):
            slots.append(Slot(f"L{level}-C{i}", SlotType.COMPACT, level))
        slots.append(Slot(f"L{level}-L1", SlotType.LARGE, level))
        slots.append(Slot(f"L{level}-B1", SlotType.TWO_WHEELER, level))
    return ParkingLot("PES Campus Lot", slots)


class Console:
    def __init__(self, lot, ask=input, say=print, clock=datetime.now):
        self.lot, self.ask, self.say, self.clock = lot, ask, say, clock
        self.tickets, self.reservations, self.payments = {}, {}, {}
        self.gateway = billing.MockGateway()

    def _vehicle(self):
        plate = self.ask("Number plate: ")
        vtype = TYPES.get(self.ask("Type (bike/car/suv): ").strip().lower())
        if vtype is None:
            raise ParkingError("Vehicle type must be bike, car or suv")
        is_ev = self.ask("Electric vehicle? (y/n): ").strip().lower() == "y"
        return Vehicle(plate, vtype, is_ev)

    def entry(self):
        t = entry_exit.vehicle_entry(self.lot, self._vehicle(), self.clock(), self.tickets)
        level = self.lot.get_slot(t.slot_id).level
        self.say(f"Ticket {t.ticket_id} -> slot {t.slot_id} (level {level})")

    def exit(self):
        t = entry_exit.vehicle_exit(self.lot, self.ask("Ticket id: ").strip(), self.clock(), self.tickets)
        self.say(f"Goodbye {t.plate}. Slot {t.slot_id} is now free.")

    def pay(self):
        ticket_id = self.ask("Ticket id: ").strip()
        ticket = self.tickets.get(ticket_id)
        if ticket is None:
            raise ParkingError(f"Unknown ticket {ticket_id!r}")
        ticket.amount_due = billing.calculate_fee(ticket.vehicle_type, ticket.entry_time, self.clock())
        self.say(f"Amount due: Rs {ticket.amount_due:.0f}")
        try:
            amount = float(self.ask("Amount paid: "))
        except ValueError:
            raise ParkingError("Amount must be a number")
        method = self.ask("Method (cash/upi/card): ").strip() or "cash"
        payment = billing.pay(ticket, amount, self.gateway, method, now=self.clock())
        self.payments[ticket_id] = payment
        self.say(billing.receipt(ticket, payment))

    def reserve(self):
        vehicle = self._vehicle()
        minutes = int(self.ask("Arriving in how many minutes? ") or 0)
        start = self.clock() + timedelta(minutes=minutes)
        r = reservations.create(self.lot, vehicle, start, self.reservations)
        self.say(f"Reservation {r.reservation_id} holds slot {r.slot_id} from {r.start_time:%H:%M}")

    def cancel(self):
        r = reservations.cancel(self.lot, self.ask("Reservation id: ").strip(), self.reservations)
        self.say(f"Reservation cancelled; slot {r.slot_id} released.")

    def check_in(self):
        rid = self.ask("Reservation id: ").strip()
        t = reservations.check_in(self.lot, rid, self.clock(), self.reservations, self.tickets)
        self.say(f"Ticket {t.ticket_id} -> reserved slot {t.slot_id}")

    def occupancy(self):
        o = self.lot.occupancy()
        self.say(f"Total {o['total']} | occupied {o['occupied']} | reserved {o['reserved']} | available {o['available']}")

    def report(self):
        for level, types in sorted(reports.occupancy_by_level_and_type(self.lot).items()):
            for kind, row in sorted(types.items()):
                self.say(f"Level {level} {kind:<12} free {row['available']}/{row['total']}")

    def run(self):
        actions = {"1": self.entry, "2": self.exit, "3": self.pay, "4": self.reserve,
                   "5": self.cancel, "6": self.occupancy, "7": self.report, "8": self.check_in}
        self.say(f"Smart Parking Management System - {self.lot.name}")
        while True:
            reservations.expire_no_shows(self.lot, self.clock(), self.reservations)
            self.say(MENU)
            choice = self.ask("Choose: ").strip()
            if choice == "0":
                self.say("Bye.")
                return
            action = actions.get(choice)
            if action is None:
                self.say("Please choose a number from the menu.")
                continue
            try:
                action()
            except (ParkingError, ValueError) as err:
                self.say(f"Error: {err}")


def main():
    Console(build_demo_lot()).run()


if __name__ == "__main__":
    main()
