# Feature allocation

Each member owns **one module file** and **4 features**, so PRs rarely touch the same file.
Feature IDs (`SPMS-F-0xx`) match the SRS, Test Plan and RTM. Test functions are named after
their test case id, e.g. `test_tc_alc_01_suv_only_gets_large`.

Every feature = one branch = one PR = at least one test.
`SPMS-F-001` (real-time occupancy summary) is already on `main` as the baseline.

## Shared conventions
- Errors come from `smart_parking/errors.py` (`ParkingError` and subclasses). Services raise, the console prints.
- Services never call `datetime.now()`; the current time is passed in as `now`.
- `tickets` and `reservations` are plain dicts keyed by id (`str(uuid.uuid4())`).

## Satyanarayana Kallakuri — Allocation (`smart_parking/allocation.py`)
```python
find_slot(lot, vehicle) -> Slot | None
```
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-002 | Find a compatible free slot (bike→two-wheeler, car→compact/large, SUV→large) | `feature/allocate-slot` |
| SPMS-F-003 | Prefer smallest suitable slot type, then lowest level | `feature/best-fit-allocation` |
| SPMS-F-004 | EV slots go to non-EV vehicles only if nothing else is free | `feature/ev-slot-priority` |
| SPMS-F-005 | Clear lot-full result when nothing suitable is free | `feature/lot-full` |

**F-002 goes first** — entry and reservations call `find_slot`.

## Shubham D Bhat — Entry / Exit (`smart_parking/entry_exit.py`)
```python
validate_plate(plate) -> bool
vehicle_entry(lot, vehicle, now, tickets) -> Ticket
vehicle_exit(lot, ticket_id, now, tickets) -> Ticket
```
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-006 | Validate Indian number plate format (e.g. `KA01AB1234`) | `feature/plate-validation` |
| SPMS-F-007 | Entry: allocate slot, mark occupied, issue ticket | `feature/vehicle-entry` |
| SPMS-F-008 | Reject duplicate entry of a plate already inside | `feature/duplicate-entry` |
| SPMS-F-009 | Exit: set exit time, release slot; refuse if amount due is unpaid | `feature/vehicle-exit` |

## Sujan S M — Reservations (`smart_parking/reservations.py`)
```python
create(lot, vehicle, start, reservations) -> Reservation
cancel(lot, reservation_id, reservations) -> Reservation
expire_no_shows(lot, now, reservations) -> int
check_in(lot, reservation_id, now, reservations, tickets) -> Ticket
```
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-010 | Create a reservation that holds a slot | `feature/create-reservation` |
| SPMS-F-011 | Cancel a reservation and release its slot | `feature/cancel-reservation` |
| SPMS-F-012 | Expire no-shows 15 min after start time | `feature/reservation-expiry` |
| SPMS-F-013 | Check in with a reservation id → ticket for the held slot | `feature/reservation-checkin` |

## Siddanth Anil — Billing & Reports (`smart_parking/billing.py`, `smart_parking/reports.py`)
```python
calculate_fee(vehicle_type, entry, exit) -> float
pay(ticket, amount, gateway) -> Payment
receipt(ticket, payment) -> str
occupancy_by_level_and_type(lot) -> dict
```
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-014 | Fee: 15 min free, ₹10/₹30/₹40 per started hour (bike/car/SUV), daily cap 8× rate | `feature/fee-calculation` |
| SPMS-F-015 | Pay exact amount through gateway interface (mock), mark ticket paid | `feature/payment` |
| SPMS-F-016 | Receipt text for a paid ticket | `feature/receipt` |
| SPMS-F-017 | Occupancy report by level and slot type | `feature/occupancy-report` |

## Order that avoids blocking
1. Setup PR (errors, coverage, this file).
2. Round 1: F-002, F-006, F-014 in parallel → then F-010 once F-002 is merged.
3. Round 2: F-007 (needs F-002), F-003, F-011, F-015.
4. Rounds 3–4: the rest. Each member adds their menu option to `main.py` in their last PR.

## Review rotation
Satyanarayana → Shubham → Sujan → Siddanth → Satyanarayana (author requests the next person).
