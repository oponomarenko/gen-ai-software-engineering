"""Validation rules for transaction fields."""

from decimal import Decimal
from datetime import datetime

import pycountry

VALID_CURRENCIES: frozenset[str] = frozenset(
    c.alpha_3 for c in pycountry.currencies
)


def validate_amount(v: float) -> float:
    if v <= 0:
        raise ValueError("Amount must be a positive number")
    if Decimal(str(v)).as_tuple().exponent < -2:
        raise ValueError("Amount must have at most 2 decimal places")
    return v


def validate_currency(v: str) -> str:
    if v not in VALID_CURRENCIES:
        raise ValueError("Invalid currency code")
    return v


def validate_timestamp(v: datetime | None) -> datetime | None:
    if v is not None and v.tzinfo is None:
        raise ValueError("timestamp must include timezone info (e.g. 2024-01-15T10:30:00Z)")
    return v
