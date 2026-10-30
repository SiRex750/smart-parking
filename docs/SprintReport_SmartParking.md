# Sprint Report — Smart Parking Management System

Backlog, sprint plan and outcomes for SE Mini-Project Parts 2 and 3. The backlog lives in this repo's
[Issues](https://github.com/SiRex750/smart-parking/issues) (one per SRS requirement, labelled `SP: n` for story points
and `type: FR / NFR / security / testing`) and is grouped into the
[Sprint milestones](https://github.com/SiRex750/smart-parking/milestones?state=all).

## Backlog summary

| | Items | Story points |
|---|---|---|
| Sprint-1 (19–23 Oct) | 14 | 40 |
| Sprint-2 (26–30 Oct) | 10 | 32 |
| Sprint-3 (2–6 Nov, testing) | 6 | 12 |
| Deferred (not in v1.0) | 4 | 16 |
| **Total** | **34** | **100** |

Story points per member: Siddanth 27, Shubham 26, Sujan 25, Satyanarayana 22.
Scale: 1 = trivial, 2 = small, 3 = medium, 5 = large, 8 = very large.

## Sprint-1 — core parking flow (19–23 Oct 2026)

**Goal:** a working product where a vehicle can enter, get the best slot, pay and exit.
**Outcome:** goal met — all 14 items closed (40 points).

| Issue | Item | Type | SP | Owner | Delivered by |
|---|---|---|---|---|---|
| #22 | SPMS-F-001 Real-time occupancy summary | FR | 2 | Siddanth | initial commit |
| #23 | SPMS-F-002 Find compatible slot | FR | 3 | Satyanarayana | #2 |
| #24 | SPMS-F-003 Best-fit allocation | FR | 3 | Satyanarayana | #5 |
| #25 | SPMS-F-004 EV slot priority | FR | 3 | Satyanarayana | #10 |
| #26 | SPMS-F-005 Lot-full handling | FR | 2 | Satyanarayana | #14 |
| #27 | SPMS-F-006 Plate validation | FR | 2 | Shubham | #3 |
| #28 | SPMS-F-007 Vehicle entry | FR | 5 | Shubham | #6 |
| #29 | SPMS-F-008 Duplicate entry prevention | FR | 2 | Shubham | #11 |
| #30 | SPMS-F-009 Vehicle exit | FR | 5 | Shubham | #15 |
| #35 | SPMS-F-014 Fee calculation | FR | 3 | Siddanth | #4 |
| #36 | SPMS-F-015 Payment processing | FR | 5 | Siddanth | #8 |
| #42 | SPMS-NF-004 Maintainability | NFR | 2 | Siddanth | #1, #19 |
| #48 | SPMS-SR-004 Validate all external input | Security | 2 | Shubham | #3, #8, #12 |
| #50 | SPMS-SR-006 Random UUID ids | Security | 1 | Sujan | #6, #7, #19 |

## Sprint-2 — reservations, reports, console, NFRs (26–30 Oct 2026)

**Goal:** reservations end to end, receipts and reports, a usable operator console, and the non-functional tests.
**Outcome:** goal met — all 10 items closed (32 points). Development frozen after this sprint.

| Issue | Item | Type | SP | Owner | Delivered by |
|---|---|---|---|---|---|
| #31 | SPMS-F-010 Create reservation | FR | 5 | Sujan | #7 |
| #32 | SPMS-F-011 Cancel reservation | FR | 2 | Sujan | #12 |
| #33 | SPMS-F-012 No-show expiry | FR | 3 | Sujan | #16 |
| #34 | SPMS-F-013 Reservation check-in | FR | 5 | Sujan | #17 |
| #37 | SPMS-F-016 Receipt | FR | 2 | Siddanth | #13 |
| #38 | SPMS-F-017 Occupancy report | FR | 3 | Siddanth | #9 |
| #39 | SPMS-NF-001 Performance | NFR | 3 | Satyanarayana | #19 |
| #40 | SPMS-NF-002 Performance / Real-time | NFR | 1 | Siddanth | #19 |
| #41 | SPMS-NF-003 Reliability | NFR | 5 | Sujan | #19 |
| #43 | SPMS-NF-005 Usability | NFR | 3 | Shubham | #18, #19 |

## Sprint-3 — testing and reports (2–6 Nov 2026, Part-3)

| Issue | Item | Type | SP | Owner | Delivered by |
|---|---|---|---|---|---|
| #44 | SPMS-NF-006 Portability | NFR | 2 | Sujan | — |
| #51 | Update test cases after the sprints | Testing | 2 | Sujan | — |
| #52 | Unit Test Report | Testing | 2 | Shubham | — |
| #53 | System Validation Report | Testing | 3 | Satyanarayana | — |
| #54 | Code Coverage Report | Testing | 1 | Siddanth | — |
| #55 | Branch Coverage Report | Testing | 2 | Siddanth | — |

## Deferred backlog (not in v1.0)

| Issue | Item | Type | SP | Owner | Delivered by |
|---|---|---|---|---|---|
| #45 | SPMS-SR-001 TLS 1.2+ on all connections | Security | 3 | Siddanth | — |
| #46 | SPMS-SR-002 Admin-only configuration | Security | 5 | Satyanarayana | — |
| #47 | SPMS-SR-003 No card data stored | Security | 3 | Siddanth | — |
| #49 | SPMS-SR-005 Append-only audit log | Security | 5 | Shubham | — |

## Deviations from the submitted documents and plan

These are explained at the final demo (Part-2 §2.i).

1. **Timing.** All feature code was written and merged on 10–11 Oct 2026, before the sprint windows, while the
   GitHub workflow was being set up. The backlog and sprint milestones were created afterwards from the SRS, and
   each issue links to the pull request that delivered it, so the PR timestamps show the real dates.
   Sprint-1 and Sprint-2 were used to review, test and demo the delivered increments rather than to write new code.
2. **Who raised the PRs.** Every PR was opened from the repo owner's account (SiRex750) and reviewed and merged by a
   teammate (satk4ll, Shubhambhat06, sujan1001) — the reverse of Part-2 §2.c/§2.d. Ownership of each module is
   recorded in `FEATURES.md` and in the issue assignees.
3. **Security requirements.** SPMS-SR-001, SR-002, SR-003 and SR-005 (TLS, admin roles, card-data checks, audit log)
   are documented in the SRS/SAD but not implemented in v1.0; they stay open in the backlog with the `deferred` label.
4. **Ticket model.** `Ticket.vehicle_type` was added (PR #15) so the exit fee can be computed at the gate; the SAD
   class diagram shows the original fields.
5. **Exit flow.** As in the corrected SAD sequence diagram, the Entry/Exit service (not Billing) releases the slot,
   and exit is refused until any amount due is paid.
6. **Extra API.** `allocation.require_slot()` (F-005) raises a descriptive `LotFullError`; the SAD lists only `find_slot()`.

## Sprint demo videos

| Sprint | Length | File |
|---|---|---|
| Sprint-1 | ~1 min | `docs/videos/Sprint1_Demo.mp4` (to be added) |
| Sprint-2 | ~2 min | `docs/videos/Sprint2_Demo.mp4` (to be added) |
