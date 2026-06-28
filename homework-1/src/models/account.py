from datetime import datetime

from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    accountId: str = Field(description="The queried account ID.", example="ACC-DST01")
    balances: dict[str, float] = Field(
        description="Current balance per currency. Only completed transactions are included.",
        example={"USD": 425.75, "EUR": 1200.50},
    )


class CurrencySummary(BaseModel):
    totalDeposits: float = Field(description="Sum of all completed deposits received by this account in this currency.", example=500.00)
    totalWithdrawals: float = Field(description="Sum of all completed withdrawals sent from this account in this currency.", example=150.00)


class SummaryResponse(BaseModel):
    accountId: str = Field(description="The queried account ID.", example="ACC-DST01")
    byCurrency: dict[str, CurrencySummary] = Field(
        description="Deposit and withdrawal totals broken down by currency. Only completed transactions are counted.",
    )
    transactionCount: int = Field(description="Total number of transactions involving this account (all statuses).", example=5)
    mostRecentTransactionDate: datetime = Field(
        description="Timestamp of the most recent transaction involving this account.",
        example="2024-01-15T10:30:00Z",
    )
