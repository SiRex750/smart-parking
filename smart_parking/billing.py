"""Billing and payments (SPMS-F-014..016)."""
import math
from datetime import datetime

from smart_parking.models import VehicleType

RATES = {VehicleType.BIKE: 10, VehicleType.CAR: 30, VehicleType.SUV: 40}  # ₹ per started hour
GRACE_MINUTES = 15
DAILY_CAP_HOURS = 8  # one day never costs more than 8 x the hourly rate


def calculate_fee(vehicle_type: VehicleType, entry: datetime, exit: datetime) -> float:
    """Fee in rupees for a stay from entry to exit.

    - First 15 minutes are free.
    - Each started hour is charged at the vehicle type's rate.
    - Each 24-hour block is capped at 8 x the hourly rate.
    """
    if exit < entry:
        raise ValueError("exit time is before entry time")
    minutes = (exit - entry).total_seconds() / 60
    if minutes <= GRACE_MINUTES:
        return 0.0
    rate = RATES[vehicle_type]
    cap = DAILY_CAP_HOURS * rate
    full_days, rest = divmod(minutes, 24 * 60)
    fee = full_days * cap + min(math.ceil(rest / 60) * rate, cap)
    return float(fee)
