"""Vehicle entry and exit (SPMS-F-006..009)."""
import re

# 2 letters (state), 1-2 digits (RTO), 0-3 letters (series), 4 digits (number)
PLATE_PATTERN = re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{4}$")


def validate_plate(plate) -> bool:
    """Return True if plate is a valid Indian number plate, e.g. KA01AB1234.

    Surrounding whitespace is ignored and letters are compared in upper case.
    """
    if not isinstance(plate, str):
        return False
    return bool(PLATE_PATTERN.match(plate.strip().upper()))
