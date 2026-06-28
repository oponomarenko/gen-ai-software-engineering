"""Routes for /transactions."""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.models import Transaction, TransactionCreate, TransactionType
from src import storage

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=Transaction, status_code=201)
def create_transaction(body: TransactionCreate) -> Transaction:
    tx = Transaction(
        id=str(uuid.uuid4()),
        fromAccount=body.fromAccount,
        toAccount=body.toAccount,
        amount=body.amount,
        currency=body.currency,
        type=body.type,
        timestamp=body.timestamp or datetime.now(timezone.utc),
        status=body.status,
    )
    return storage.add_transaction(tx)


@router.get("", response_model=list[Transaction])
def list_transactions(
    accountId: Optional[str] = None,
    type: Optional[TransactionType] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
) -> list[Transaction]:
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(status_code=400, detail={"error": "Invalid date range", "details": [{"field": "from", "message": "'from' must not be after 'to'"}]})
    return storage.filter_transactions(
        storage.list_transactions(),
        account_id=accountId,
        type_=type,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str) -> Transaction:
    tx = storage.get_transaction(transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail={"error": "Transaction not found"})
    return tx
