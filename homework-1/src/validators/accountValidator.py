"""Validation rules for account fields."""

import re

ACCOUNT_RE = re.compile(r"^ACC-[A-Z0-9]{5}$")


def validate_account_id(v: str) -> str:
    if not ACCOUNT_RE.match(v):
        raise ValueError("Account ID must match pattern ACC-XXXXX (5 uppercase alphanumeric characters)")
    return v
