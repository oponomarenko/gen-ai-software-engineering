from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator

from src.validators.transactionValidator import (
    ACCOUNT_RE,
    VALID_CURRENCIES,
    validate_amount,
    validate_currency,
)


class TransactionType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class TransactionStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class TransactionCreate(BaseModel):
    fromAccount: str
    toAccount: str
    amount: float
    currency: str
    type: TransactionType
    timestamp: datetime | None = None
    status: TransactionStatus = TransactionStatus.completed

    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: float) -> float:
        return validate_amount(v)

    @field_validator("fromAccount", "toAccount")
    @classmethod
    def check_account_format(cls, v: str) -> str:
        if not ACCOUNT_RE.match(v):
            raise ValueError("Account ID must match pattern ACC-XXXXX (5 uppercase alphanumeric characters)")
        return v

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v: str) -> str:
        return validate_currency(v)


class Transaction(BaseModel):
    id: str
    fromAccount: str
    toAccount: str
    amount: float
    currency: str
    type: TransactionType
    timestamp: datetime
    status: TransactionStatus
