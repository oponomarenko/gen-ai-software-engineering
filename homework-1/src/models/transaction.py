from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

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
    fromAccount: str = Field(description="Sender account ID. Must match pattern ACC-XXXXX.", example="ACC-SRC01")
    toAccount: str = Field(description="Receiver account ID. Must match pattern ACC-XXXXX.", example="ACC-DST01")
    amount: float = Field(description="Transaction amount. Must be positive with at most 2 decimal places.", example=250.00)
    currency: str = Field(description="ISO 4217 currency code (e.g. USD, EUR, GBP).", example="USD")
    type: TransactionType = Field(description="Transaction type: deposit, withdrawal, or transfer.")
    timestamp: datetime | None = Field(
        default=None,
        description="Transaction timestamp in ISO 8601 format. Defaults to the current UTC time if omitted.",
        example="2024-01-15T10:30:00Z",
    )
    status: TransactionStatus = Field(
        default=TransactionStatus.completed,
        description="Transaction status. Defaults to `completed` if omitted.",
    )

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
    id: str = Field(description="Auto-generated UUID uniquely identifying the transaction.", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    fromAccount: str = Field(description="Sender account ID.", example="ACC-SRC01")
    toAccount: str = Field(description="Receiver account ID.", example="ACC-DST01")
    amount: float = Field(description="Transaction amount.", example=250.00)
    currency: str = Field(description="ISO 4217 currency code.", example="USD")
    type: TransactionType = Field(description="Transaction type.")
    timestamp: datetime = Field(description="Transaction timestamp (UTC).", example="2024-01-15T10:30:00Z")
    status: TransactionStatus = Field(description="Transaction status.")
