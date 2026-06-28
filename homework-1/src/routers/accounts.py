"""Routes for /accounts."""

from fastapi import APIRouter, HTTPException

from src import storage
from src.models import BalanceResponse, CurrencySummary, SummaryResponse, TransactionStatus, TransactionType
from src.validators.accountValidator import ACCOUNT_RE

router = APIRouter(prefix="/accounts", tags=["accounts"])


def _validate_account_id(account_id: str) -> None:
    if not ACCOUNT_RE.match(account_id):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid account ID format", "message": "Account ID must match pattern ACC-XXXXX"},
        )


@router.get("/{account_id}/balance", response_model=BalanceResponse)
def get_balance(account_id: str) -> BalanceResponse:
    _validate_account_id(account_id)
    txs = [
        tx for tx in storage.list_transactions()
        if tx.fromAccount == account_id or tx.toAccount == account_id
    ]
    if not txs:
        raise HTTPException(status_code=404, detail={"error": "Account not found"})

    balances: dict[str, float] = {}
    for tx in txs:
        if tx.status != TransactionStatus.completed:
            continue
        c = tx.currency
        balances.setdefault(c, 0.0)
        if tx.toAccount == account_id:
            balances[c] += tx.amount
        if tx.fromAccount == account_id:
            balances[c] -= tx.amount

    return BalanceResponse(
        accountId=account_id,
        balances={c: round(b, 2) for c, b in balances.items()},
    )


@router.get("/{account_id}/summary", response_model=SummaryResponse)
def get_summary(account_id: str) -> SummaryResponse:
    _validate_account_id(account_id)
    txs = [
        tx for tx in storage.list_transactions()
        if tx.fromAccount == account_id or tx.toAccount == account_id
    ]
    if not txs:
        raise HTTPException(status_code=404, detail={"error": "Account not found"})

    by_currency: dict[str, dict[str, float]] = {}
    for tx in txs:
        if tx.status != TransactionStatus.completed:
            continue
        c = tx.currency
        if c not in by_currency:
            by_currency[c] = {"totalDeposits": 0.0, "totalWithdrawals": 0.0}
        if tx.type == TransactionType.deposit and tx.toAccount == account_id:
            by_currency[c]["totalDeposits"] += tx.amount
        elif tx.type == TransactionType.withdrawal and tx.fromAccount == account_id:
            by_currency[c]["totalWithdrawals"] += tx.amount

    currency_summaries = {
        c: CurrencySummary(
            totalDeposits=round(data["totalDeposits"], 2),
            totalWithdrawals=round(data["totalWithdrawals"], 2),
        )
        for c, data in by_currency.items()
    }

    most_recent = max(tx.timestamp for tx in txs)

    return SummaryResponse(
        accountId=account_id,
        byCurrency=currency_summaries,
        transactionCount=len(txs),
        mostRecentTransactionDate=most_recent,
    )
