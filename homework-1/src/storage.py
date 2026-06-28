"""In-memory store for transactions."""

from src.models import Transaction

_store: dict[str, Transaction] = {}


def add_transaction(tx: Transaction) -> Transaction:
    _store[tx.id] = tx
    return tx


def get_transaction(tx_id: str) -> Transaction | None:
    return _store.get(tx_id)


def list_transactions() -> list[Transaction]:
    return list(_store.values())
