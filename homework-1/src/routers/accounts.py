"""Routes for /accounts."""

from fastapi import APIRouter, HTTPException

from src import storage
from src.models import BalanceResponse, TransactionStatus

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/{account_id}/balance", response_model=BalanceResponse)
def get_balance(account_id: str) -> BalanceResponse:
    txs = [
        tx for tx in storage.list_transactions()
        if tx.fromAccount == account_id or tx.toAccount == account_id
    ]
    if not txs:
        raise HTTPException(status_code=404, detail={"error": "Account not found"})

    balance = 0.0
    currency = txs[0].currency
    for tx in txs:
        if tx.status != TransactionStatus.completed:
            continue
        if tx.toAccount == account_id:
            balance += tx.amount
        if tx.fromAccount == account_id:
            balance -= tx.amount

    return BalanceResponse(accountId=account_id, balance=round(balance, 2), currency=currency)
