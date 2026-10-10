"""Billing and payments (SPMS-F-014..016)."""
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from smart_parking.errors import PaymentError
from smart_parking.models import Ticket, VehicleType

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


# --- SPMS-F-015 payment --------------------------------------------------------
class PaymentGateway(Protocol):
    """Adapter interface for an external payment provider (SAD ADR-004)."""

    def charge(self, amount: float, method: str) -> Optional[str]:
        """Return a gateway reference if approved, or None if declined."""


class MockGateway:
    """Test/demo gateway: approves everything unless created with approve=False."""

    def __init__(self, approve: bool = True):
        self.approve = approve
        self.charges = []

    def charge(self, amount: float, method: str) -> Optional[str]:
        self.charges.append((amount, method))
        return f"MOCK-{uuid.uuid4().hex[:10].upper()}" if self.approve else None


@dataclass
class Payment:
    payment_id: str
    ticket_id: str
    amount: float
    method: str
    gateway_ref: str
    timestamp: datetime = field(default_factory=datetime.now)


def pay(ticket: Ticket, amount: float, gateway: PaymentGateway, method: str = "cash",
        now: Optional[datetime] = None) -> Payment:
    """Pay the exact amount due on a ticket through the gateway (SPMS-F-015).

    The caller sets ticket.amount_due (via calculate_fee) before paying.
    Raises PaymentError if already paid, nothing is due, the amount is wrong,
    or the gateway declines; the ticket stays unpaid on any error.
    """
    if ticket.paid:
        raise PaymentError("Ticket is already paid")
    if ticket.amount_due <= 0:
        raise PaymentError("Nothing to pay on this ticket")
    if not isinstance(amount, (int, float)) or amount != ticket.amount_due:
        raise PaymentError(f"Amount mismatch: due ₹{ticket.amount_due:.0f}, got {amount!r}")
    ref = gateway.charge(amount, method)
    if not ref:
        raise PaymentError("Payment declined by gateway")
    ticket.paid = True
    return Payment(
        payment_id=str(uuid.uuid4()),
        ticket_id=ticket.ticket_id,
        amount=float(amount),
        method=method,
        gateway_ref=ref,
        timestamp=now or datetime.now(),
    )
