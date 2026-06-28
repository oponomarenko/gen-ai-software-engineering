"""Routes for /transactions."""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.models import Transaction, TransactionCreate, TransactionType
from src import storage

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "",
    response_model=Transaction,
    status_code=201,
    summary="Create a transaction",
    description=(
        "Create a new banking transaction (deposit, withdrawal, or transfer). "
        "The `id` is auto-generated. "
        "`timestamp` defaults to the current UTC time if omitted. "
        "`status` defaults to `completed` if omitted."
    ),
    responses={
        201: {"description": "Transaction created successfully"},
        400: {"description": "Validation failed — invalid amount, account format, or currency"},
    },
)
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


@router.get(
    "",
    response_model=list[Transaction],
    summary="List transactions",
    description=(
        "Return all transactions, optionally filtered by account, type, and/or date range. "
        "All filters are combined with AND logic. "
        "Returns an empty list when no transactions match — never a 404."
    ),
    responses={
        200: {"description": "List of matching transactions (may be empty)"},
        400: {"description": "Invalid date range — `from` must not be after `to`"},
    },
)
def list_transactions(
    accountId: Optional[str] = Query(
        None,
        description="Filter by account ID — matches transactions where the account is either sender or receiver.",
        examples={"example": {"value": "ACC-DST01"}},
    ),
    type: Optional[TransactionType] = Query(
        None,
        description="Filter by transaction type: `deposit`, `withdrawal`, or `transfer`.",
    ),
    from_date: Optional[date] = Query(
        None,
        alias="from",
        description="Include only transactions on or after this date (YYYY-MM-DD).",
        examples={"example": {"value": "2024-01-01"}},
    ),
    to_date: Optional[date] = Query(
        None,
        alias="to",
        description="Include only transactions on or before this date (YYYY-MM-DD).",
        examples={"example": {"value": "2024-12-31"}},
    ),
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


@router.get(
    "/{transaction_id}",
    response_model=Transaction,
    summary="Get a transaction by ID",
    description="Retrieve a single transaction by its UUID. Returns 404 if no transaction with that ID exists.",
    responses={
        200: {"description": "Transaction found"},
        404: {"description": "Transaction not found"},
    },
)
def get_transaction(transaction_id: str) -> Transaction:
    tx = storage.get_transaction(transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail={"error": "Transaction not found"})
    return tx
