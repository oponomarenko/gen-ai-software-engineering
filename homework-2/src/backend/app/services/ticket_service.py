import uuid
from datetime import datetime, timezone

from app.core.errors import NotFoundError
from app.models.enums import Category, Priority, Status
from app.models.ticket import Ticket, TicketCreate, TicketUpdate
from app.repository.base import TicketRepository
from app.services.classification_service import ClassificationService


class TicketService:
    def __init__(self, repository: TicketRepository, classification_service: ClassificationService):
        self._repository = repository
        self._classification_service = classification_service

    def create(self, payload: TicketCreate, auto_classify: bool = False) -> Ticket:
        ticket = Ticket(**payload.model_dump())
        if auto_classify:
            result = self._classification_service.classify_ticket(ticket)
            ticket.classification = result
            ticket.category = result.category
            ticket.priority = result.priority
        return self._repository.create(ticket)

    def get(self, ticket_id: uuid.UUID) -> Ticket:
        ticket = self._repository.get(ticket_id)
        if ticket is None:
            raise NotFoundError(f"Ticket {ticket_id} not found")
        return ticket

    def list(
        self,
        category: Category | None = None,
        priority: Priority | None = None,
        status: Status | None = None,
    ) -> list[Ticket]:
        return self._repository.list(category=category, priority=priority, status=status)

    def update(self, ticket_id: uuid.UUID, payload: TicketUpdate) -> Ticket:
        ticket = self.get(ticket_id)
        updates = payload.model_dump(exclude_unset=True)
        updated = ticket.model_copy(update=updates)
        updated.updated_at = datetime.now(timezone.utc)
        if updates.get("status") == Status.resolved and ticket.resolved_at is None:
            updated.resolved_at = updated.updated_at
        if "category" in updates or "priority" in updates:
            updated.classification = self._classification_service.override(
                updated, category=updated.category, priority=updated.priority
            )
        return self._repository.update(updated)

    def delete(self, ticket_id: uuid.UUID) -> None:
        if not self._repository.delete(ticket_id):
            raise NotFoundError(f"Ticket {ticket_id} not found")

    def auto_classify(self, ticket_id: uuid.UUID) -> Ticket:
        ticket = self.get(ticket_id)
        result = self._classification_service.classify_ticket(ticket)
        ticket.classification = result
        ticket.category = result.category
        ticket.priority = result.priority
        ticket.updated_at = datetime.now(timezone.utc)
        return self._repository.update(ticket)
