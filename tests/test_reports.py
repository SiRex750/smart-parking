from smart_parking.main import build_demo_lot
from smart_parking.reports import occupancy_by_level_and_type


def test_tc_rpt_01_has_every_level_and_type():
    report = occupancy_by_level_and_type(build_demo_lot())
    assert set(report) == {0, 1}
    for level in report.values():
        assert set(level) == {"compact", "large", "two_wheeler"}
    assert report[0]["compact"]["total"] == 3


def test_tc_rpt_01_counts_match_lot_totals():
    lot = build_demo_lot()
    lot.get_slot("L0-C1").occupied_by = "KA01AB0001"
    lot.get_slot("L1-L1").occupied_by = "KA01AB0002"
    lot.get_slot("L1-B1").reserved_for = "R1"
    report = occupancy_by_level_and_type(lot)
    assert report[0]["compact"]["occupied"] == 1
    assert report[1]["large"]["occupied"] == 1
    assert report[1]["two_wheeler"]["reserved"] == 1
    totals = {k: sum(r[k] for lvl in report.values() for r in lvl.values())
              for k in ("total", "occupied", "reserved", "available")}
    assert totals == lot.occupancy()


def test_tc_rpt_01_empty_lot_gives_empty_report():
    from smart_parking.models import ParkingLot

    assert occupancy_by_level_and_type(ParkingLot("empty")) == {}
