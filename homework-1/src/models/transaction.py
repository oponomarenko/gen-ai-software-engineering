from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator

from src.validators.accountValidator import validate_account_id
from src.validators.transactionValidator import (
    VALID_CURRENCIES,
    validate_amount,
    validate_currency,
    validate_timestamp,
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
        return validate_account_id(v)

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v: str) -> str:
        return validate_currency(v)

    @field_validator("timestamp")
    @classmethod
    def check_timestamp(cls, v: datetime | None) -> datetime | None:
        return validate_timestamp(v)


class Transaction(BaseModel):
    id: str
    fromAccount: str
    toAccount: str
    amount: float
    currency: str
    type: TransactionType
    timestamp: datetime
    status: TransactionStatus
