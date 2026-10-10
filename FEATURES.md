# Feature allocation

Each member owns **one module file** and **4 features**, so PRs rarely touch the same file.
Feature IDs (`SPMS-F-0xx`) are the same IDs used in the SRS, Test Plan and RTM.
Every feature = one branch = one PR = at least one test.

`SPMS-F-001` (real-time occupancy summary) is already on `main` as the baseline.

## Member 1 — Allocation (`smart_parking/allocation.py`, `tests/test_allocation.py`)
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-002 | Find a compatible free slot for a vehicle type (bike→two-wheeler, car→compact/large, SUV→large) | `feature/allocate-slot` |
| SPMS-F-003 | Prefer the smallest suitable slot and the lowest level (don't waste large slots on cars) | `feature/best-fit-allocation` |
| SPMS-F-004 | EV slots only allocated to vehicles flagged as EV unless no other slot is free | `feature/ev-slot-priority` |
| SPMS-F-005 | Return a clear "lot full" result when nothing is free for that vehicle type | `feature/lot-full` |

**Do F-002 first** — Member 2's entry feature calls it.

## Member 2 — Entry / Exit (`smart_parking/entry_exit.py`, `tests/test_entry_exit.py`)
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-006 | Validate number plate format (e.g. `KA01AB1234`) | `feature/plate-validation` |
| SPMS-F-007 | Vehicle entry: allocate slot, mark occupied, issue `Ticket` with entry time | `feature/vehicle-entry` |
| SPMS-F-008 | Reject duplicate entry of a plate already inside | `feature/duplicate-entry` |
| SPMS-F-009 | Vehicle exit: close ticket, set exit time, free the slot | `feature/vehicle-exit` |

## Member 3 — Reservations (`smart_parking/reservations.py`, `tests/test_reservations.py`)
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-010 | Create a reservation for a vehicle type and time window; holds a slot | `feature/create-reservation` |
| SPMS-F-011 | Cancel a reservation and release its slot | `feature/cancel-reservation` |
| SPMS-F-012 | Expire no-show reservations after a grace period (e.g. 15 min) | `feature/reservation-expiry` |
| SPMS-F-013 | Check-in with a reservation id parks the vehicle in the held slot | `feature/reservation-checkin` |

## Member 4 — Billing & Reports (`smart_parking/billing.py`, `smart_parking/reports.py`, matching tests)
| ID | Feature | Branch |
|---|---|---|
| SPMS-F-014 | Fee calculation: free grace period, hourly rate per vehicle type, daily cap | `feature/fee-calculation` |
| SPMS-F-015 | Process payment (mock gateway), mark ticket paid, reject wrong amounts | `feature/payment` |
| SPMS-F-016 | Generate receipt text for a paid ticket | `feature/receipt` |
| SPMS-F-017 | Occupancy report broken down by level and slot type | `feature/occupancy-report` |

## Order that avoids blocking
1. Repo owner pushes this scaffold, then protects `main`.
2. Round 1 (parallel): F-002, F-006, F-010, F-014.
3. Round 2: F-007 (needs F-002), F-003, F-011, F-015.
4. Rounds 3–4: the rest. Each member updates `main.py`'s demo for their module in their last PR.
