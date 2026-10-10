from datetime import datetime, timedelta

import pytest

from smart_parking.billing import calculate_fee
from smart_parking.models import VehicleType

T0 = datetime(2026, 10, 10, 9, 0)


def fee(vtype, **delta):
    return calculate_fee(vtype, T0, T0 + timedelta(**delta))


@pytest.mark.parametrize(
    "vtype, delta, expected",
    [
        (VehicleType.CAR, {"minutes": 10}, 0),
        (VehicleType.CAR, {"minutes": 15}, 0),
        (VehicleType.CAR, {"minutes": 16}, 30),
        (VehicleType.CAR, {"minutes": 61}, 60),
        (VehicleType.CAR, {"hours": 10}, 240),
        (VehicleType.BIKE, {"hours": 2}, 20),
        (VehicleType.SUV, {"hours": 3}, 120),
        (VehicleType.CAR, {"hours": 24}, 240),
        (VehicleType.CAR, {"hours": 26}, 300),
    ],
)
def test_tc_bil_01_fee_rules(vtype, delta, expected):
    assert fee(vtype, **delta) == expected


def test_tc_bil_01_exit_before_entry_rejected():
    with pytest.raises(ValueError):
        calculate_fee(VehicleType.CAR, T0, T0 - timedelta(minutes=1))
