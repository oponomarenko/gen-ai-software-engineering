"""In-memory store for transactions."""

from datetime import date
from typing import Optional

from src.models import Transaction, TransactionType

_store: dict[str, Transaction] = {}


def add_transaction(tx: Transaction) -> Transaction:
    _store[tx.id] = tx
    return tx


def get_transaction(tx_id: str) -> Transaction | None:
    return _store.get(tx_id)


def list_transactions() -> list[Transaction]:
    return list(_store.values())


def filter_transactions(
    txs: list[Transaction],
    *,
    account_id: Optional[str] = None,
    type_: Optional[TransactionType] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> list[Transaction]:
    result = txs
    if account_id is not None:
        result = [t for t in result if t.fromAccount == account_id or t.toAccount == account_id]
    if type_ is not None:
        result = [t for t in result if t.type == type_]
    if from_date is not None:
        result = [t for t in result if t.timestamp.date() >= from_date]
    if to_date is not None:
        result = [t for t in result if t.timestamp.date() <= to_date]
    return result
