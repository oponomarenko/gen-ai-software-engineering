"""Validation rules for transaction fields."""

import re
from decimal import Decimal

import pycountry

VALID_CURRENCIES: frozenset[str] = frozenset(
    c.alpha_3 for c in pycountry.currencies
)

ACCOUNT_RE = re.compile(r"^ACC-[A-Z0-9]{5}$")


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
