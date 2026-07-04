import uuid
from abc import ABC, abstractmethod

from app.models.enums import Category, Priority, Status
from app.models.ticket import Ticket


class TicketRepository(ABC):
    """Storage seam for tickets. Swap the implementation to change persistence
    without touching the service or API layers."""

    @abstractmethod
    def create(self, ticket: Ticket) -> Ticket: ...

    @abstractmethod
    def get(self, ticket_id: uuid.UUID) -> Ticket | None: ...

    @abstractmethod
    def list(
        self,
        category: Category | None = None,
        priority: Priority | None = None,
        status: Status | None = None,
    ) -> list[Ticket]: ...

    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket: ...

    @abstractmethod
    def delete(self, ticket_id: uuid.UUID) -> bool: ...
