import threading
import uuid

from app.models.enums import Category, Priority, Status
from app.models.ticket import Ticket
from app.repository.base import TicketRepository


class InMemoryTicketRepository(TicketRepository):
    """Thread-safe dict-backed store keyed by ticket UUID."""

    def __init__(self) -> None:
        self._tickets: dict[uuid.UUID, Ticket] = {}
        self._lock = threading.Lock()

    def create(self, ticket: Ticket) -> Ticket:
        with self._lock:
            self._tickets[ticket.id] = ticket
        return ticket

    def get(self, ticket_id: uuid.UUID) -> Ticket | None:
        with self._lock:
            return self._tickets.get(ticket_id)

    def list(
        self,
        category: Category | None = None,
        priority: Priority | None = None,
        status: Status | None = None,
    ) -> list[Ticket]:
        with self._lock:
            tickets = list(self._tickets.values())
        if category is not None:
            tickets = [t for t in tickets if t.category == category]
        if priority is not None:
            tickets = [t for t in tickets if t.priority == priority]
        if status is not None:
            tickets = [t for t in tickets if t.status == status]
        return sorted(tickets, key=lambda t: t.created_at)

    def update(self, ticket: Ticket) -> Ticket:
        with self._lock:
            self._tickets[ticket.id] = ticket
        return ticket

    def delete(self, ticket_id: uuid.UUID) -> bool:
        with self._lock:
            return self._tickets.pop(ticket_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._tickets.clear()
