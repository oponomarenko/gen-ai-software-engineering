from datetime import datetime

from pydantic import BaseModel


class BalanceResponse(BaseModel):
    accountId: str
    balances: dict[str, float]


class CurrencySummary(BaseModel):
    totalDeposits: float
    totalWithdrawals: float


class SummaryResponse(BaseModel):
    accountId: str
    byCurrency: dict[str, CurrencySummary]
    transactionCount: int
    mostRecentTransactionDate: datetime
