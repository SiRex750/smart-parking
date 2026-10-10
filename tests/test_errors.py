import pytest

from smart_parking import errors

SUBCLASSES = [
    errors.InvalidPlateError,
    errors.DuplicateEntryError,
    errors.LotFullError,
    errors.UnpaidTicketError,
    errors.ReservationError,
    errors.PaymentError,
]


@pytest.mark.parametrize("exc", SUBCLASSES)
def test_every_error_is_a_parking_error(exc):
    assert issubclass(exc, errors.ParkingError)


def test_errors_carry_message():
    with pytest.raises(errors.ParkingError, match="full"):
        raise errors.LotFullError("Lot full for SUV")
