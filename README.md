# Smart Parking Management System (SPMS)

![CI](https://github.com/SiRex750/smart-parking/actions/workflows/ci.yml/badge.svg)

Tracks parking availability, vehicle entry/exit, reservations and payments. Automatically allocates suitable spaces and provides real-time occupancy information.

SE Mini Project — PES University. Python 3.12 + pytest, CI on GitHub Actions.

## Team

| Member | SRN | Module |
|---|---|---|
| Satyanarayana Kallakuri | PES1UG24AM257 | Allocation (`allocation.py`) |
| Shubham D Bhat | PES1UG24AM273 | Entry / Exit (`entry_exit.py`) |
| Sujan S M | PES1UG24AM292 | Reservations (`reservations.py`) |
| Siddanth Anil | PES1UG24AM274 | Billing & Reports (`billing.py`, `reports.py`) |

## Documents (`docs/`)

| Deliverable | File |
|---|---|
| Software Requirements Specification (v1.1, with RTM) | [docs/SRS_SmartParking.docx](docs/SRS_SmartParking.docx) |
| Software Architecture & Design | [docs/SAD_SmartParking.docx](docs/SAD_SmartParking.docx) |
| Software Test Plan (v1.1) | [docs/TestPlan_SmartParking.docx](docs/TestPlan_SmartParking.docx) |
| Test Summary Report | [docs/TestSummaryReport_SmartParking.docx](docs/TestSummaryReport_SmartParking.docx) |
| UML diagrams (PlantUML source + PNG) | [docs/diagrams/](docs/diagrams) |

## Status

- **17 / 17 functional requirements** implemented (`SPMS-F-001` … `SPMS-F-017`, see [FEATURES.md](FEATURES.md))
- **103 tests**, all passing; **98% line coverage** (CI fails below 80%)
- **19 pull requests**, each merged only after CI passed and a teammate approved

## Run it

```bash
git clone https://github.com/SiRex750/smart-parking.git
cd smart-parking
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

pytest                         # run all tests
python -m smart_parking.main   # operator console
```

Console menu: `1` entry · `2` exit · `3` pay (prints receipt) · `4` reserve · `5` cancel reservation · `6` occupancy · `7` report by level · `8` check in reservation · `0` quit.

Fee rules: first 15 minutes free, then ₹10 / ₹30 / ₹40 per started hour (bike / car / SUV), capped at 8× the hourly rate per 24 hours.

## Project layout

```
smart_parking/
  models.py        # shared data model (Vehicle, Slot, Ticket, ParkingLot)
  errors.py        # ParkingError hierarchy
  allocation.py    # best-fit slot allocation, EV priority, lot-full
  entry_exit.py    # plate validation, entry, duplicate check, exit
  reservations.py  # create, cancel, no-show expiry, check-in
  billing.py       # fees, payment via gateway adapter, receipts
  reports.py       # occupancy by level and slot type
  main.py          # operator console
tests/             # unit, integration, console and NFR tests (named after Test Plan ids)
docs/              # SRS, SAD, Test Plan, Test Summary Report, UML
.github/workflows/ci.yml  # pytest + coverage on every PR and push to main
```

## Team rules

1. One common repo; everyone is a collaborator. **Clone, don't fork.**
2. `main` is protected (ruleset "Protect main"): no direct pushes, no force pushes.
3. One feature = one branch `feature/<name>` = one PR, with at least one test.
4. Run `pytest` locally before every push.
5. A PR merges only when CI (`test`) passes **and** at least one teammate has approved it.
6. After any merge, everyone pulls the latest `main` before starting the next feature.

```
git checkout main && git pull origin main
git checkout -b feature/<name>
  ... code + test ...
pytest
git add . && git commit -m "SPMS-F-0xx: <description>"
git push origin feature/<name>
→ Pull Request → CI ✓ + 1 approval ✓ → Merge
git checkout main && git pull origin main
```
