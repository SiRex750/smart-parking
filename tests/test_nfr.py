"""Non-functional tests: performance (NF-001/002), reliability (NF-003), ids (SR-006)."""
import random
import time
import uuid
from datetime import datetime, timedelta

from smart_parking import entry_exit, reservations
from smart_parking.allocation import find_slot
from smart_parking.errors import ParkingError
from smart_parking.models import ParkingLot, Slot, SlotType, Vehicle, VehicleType

T0 = datetime(2026, 10, 11, 9, 0)
TYPES = [VehicleType.BIKE, VehicleType.CAR, VehicleType.SUV]


def big_lot(n):
    kinds = [SlotType.COMPACT] * 6 + [SlotType.LARGE] * 2 + [SlotType.TWO_WHEELER] * 2
    return ParkingLot("big", [Slot(f"S{i}", kinds[i % 10], level=i // 100, is_ev=(i % 25 == 0))
                              for i in range(n)])


def test_tc_perf_01_allocation_under_200ms_on_1000_slots():
    lot = big_lot(1000)
    for slot in lot.slots[:900]:
        slot.occupied_by = "X"
    car = Vehicle("KA01AB1234", VehicleType.CAR)
    times = []
    for _ in range(100):
        start = time.perf_counter()
        find_slot(lot, car)
        times.append(time.perf_counter() - start)
    p95 = sorted(times)[94]
    assert p95 < 0.2, f"95th percentile {p95 * 1000:.1f} ms"


def test_tc_perf_02_occupancy_reflects_changes_immediately():
    lot, tickets = big_lot(50), {}
    t = entry_exit.vehicle_entry(lot, Vehicle("KA01AB1234", VehicleType.CAR), T0, tickets)
    assert lot.occupancy()["occupied"] == 1
    entry_exit.vehicle_exit(lot, t.ticket_id, T0 + timedelta(minutes=5), tickets)
    assert lot.occupancy()["occupied"] == 0


def test_tc_rel_01_no_double_allocation_under_random_load():
    rng = random.Random(42)
    lot, tickets, res = big_lot(200), {}, {}
    now = T0
    for i in range(10_000):
        now += timedelta(minutes=1)
        op = rng.random()
        try:
            if op < 0.45:
                v = Vehicle(f"KA{rng.randint(1, 99):02d}AB{rng.randint(0, 9999):04d}", rng.choice(TYPES))
                entry_exit.vehicle_entry(lot, v, now, tickets)
            elif op < 0.75 and tickets:
                t = rng.choice([t for t in tickets.values() if t.exit_time is None] or [None])
                if t:
                    t.paid = True
                    entry_exit.vehicle_exit(lot, t.ticket_id, now, tickets)
            elif op < 0.9:
                v = Vehicle(f"MH{rng.randint(1, 99):02d}XY{rng.randint(0, 9999):04d}", rng.choice(TYPES))
                reservations.create(lot, v, now + timedelta(minutes=10), res)
            elif res:
                reservations.cancel(lot, rng.choice(list(res)), res)
        except ParkingError:
            pass
        if i % 50 == 0:
            reservations.expire_no_shows(lot, now, res)

        # invariants: a slot is never both occupied and reserved,
        # and every open ticket matches exactly one occupied slot
        open_tickets = [t for t in tickets.values() if t.exit_time is None]
        occupied = [s for s in lot.slots if s.occupied_by]
        assert not any(s.occupied_by and s.reserved_for for s in lot.slots)
        assert len(occupied) == len(open_tickets)
        assert len({t.slot_id for t in open_tickets}) == len(open_tickets)
    occ = lot.occupancy()
    assert occ["occupied"] + occ["reserved"] + occ["available"] == occ["total"]


def test_tc_sec_05_ids_are_random_uuid4():
    lot, tickets = big_lot(1000), {}
    for i in range(500):
        entry_exit.vehicle_entry(lot, Vehicle(f"KA01AB{i:04d}", VehicleType.CAR), T0, tickets)
    ids = list(tickets)
    assert len(set(ids)) == 500
    assert all(uuid.UUID(i).version == 4 for i in ids)
