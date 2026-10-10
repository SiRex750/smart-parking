import pytest

from smart_parking.entry_exit import validate_plate


@pytest.mark.parametrize("plate", ["KA01AB1234", "MH12XY0001", "DL3C1234", "KA05MN4321"])
def test_tc_ent_01_valid_plates(plate):
    assert validate_plate(plate)


def test_tc_ent_01_lowercase_and_spaces_are_normalised():
    assert validate_plate("  ka01ab1234 ")


@pytest.mark.parametrize(
    "plate",
    ["", "1234", "KA-01-AB-1234", "KA01AB12345", "KA01 AB 1234", "KA01'; DROP", None, 1234],
)
def test_tc_ent_01_invalid_plates(plate):
    assert not validate_plate(plate)
