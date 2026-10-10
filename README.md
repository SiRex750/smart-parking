# Smart Parking Management System

Tracks parking availability, vehicle entry/exit, reservations and payments. Automatically allocates suitable spaces and provides real-time occupancy information.

SE Mini Project — 4-member team. Python 3.12 + pytest, CI on GitHub Actions.

## Project layout
```
smart_parking/
  models.py        # shared data model (Vehicle, Slot, Ticket, ParkingLot)
  main.py          # demo: python -m smart_parking.main
  allocation.py    # Member 1 (to be added)
  entry_exit.py    # Member 2 (to be added)
  reservations.py  # Member 3 (to be added)
  billing.py, reports.py  # Member 4 (to be added)
tests/             # one test file per module
.github/workflows/ci.yml  # runs pytest on every PR and push to main
```
See **FEATURES.md** for who builds what.

## Team rules
1. One common repo; everyone is a collaborator. **Clone, don't fork.**
2. `main` is protected: no direct pushes. All changes arrive through Pull Requests.
3. One feature = one branch `feature/<name>` = one PR, with at least one test.
4. Run `pytest` locally before every push.
5. A PR merges only when CI is green **and** at least one teammate has approved it.
6. After any merge, everyone pulls the latest `main` before starting the next feature.

## First-time setup (every teammate)
```bash
git clone https://github.com/<owner>/smart-parking.git
cd smart-parking
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Workflow for every feature
```
git checkout main
git pull origin main
git checkout -b feature/<name>
  ... write code + test ...
pytest
git add .
git commit -m "SPMS-F-0xx: <short description>"
git push origin feature/<name>
→ open Pull Request into main on GitHub, request a teammate as reviewer
→ CI "test" check passes ✓ + 1 approval ✓
→ Merge
git checkout main
git pull origin main
```
