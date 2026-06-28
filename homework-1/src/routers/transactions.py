"""Routes for /transactions."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from src.models import Transaction, TransactionCreate
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
def list_transactions() -> list[Transaction]:
    return storage.list_transactions()


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str) -> Transaction:
    tx = storage.get_transaction(transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx
