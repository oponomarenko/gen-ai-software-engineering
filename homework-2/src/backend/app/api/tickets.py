import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.deps import get_import_service, get_ticket_service
from app.core.config import settings
from app.core.errors import BadRequestError
from app.models.enums import Category, Priority, Status
from app.models.import_summary import ImportSummary
from app.models.ticket import ClassificationResult, Ticket, TicketCreate, TicketUpdate
from app.services.import_service import ImportService
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    auto_classify: bool = Query(default=False),
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    return service.create(payload, auto_classify=auto_classify)


@router.post("/import", response_model=ImportSummary)
async def import_tickets(
    file: UploadFile = File(...),
    auto_classify: bool = Query(default=True),
    service: ImportService = Depends(get_import_service),
) -> ImportSummary:
    content = await file.read()
    if len(content) > settings.max_import_file_size_bytes:
        raise BadRequestError(
            f"File exceeds maximum size of {settings.max_import_file_size_bytes} bytes"
        )
    return service.import_file(
        content=content,
        filename=file.filename,
        content_type=file.content_type,
        auto_classify=auto_classify,
    )


@router.get("", response_model=list[Ticket])
def list_tickets(
    category: Category | None = None,
    priority: Priority | None = None,
    status: Status | None = None,
    service: TicketService = Depends(get_ticket_service),
) -> list[Ticket]:
    return service.list(category=category, priority=priority, status=status)


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(
    ticket_id: uuid.UUID,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    return service.get(ticket_id)


@router.put("/{ticket_id}", response_model=Ticket)
def update_ticket(
    ticket_id: uuid.UUID,
    payload: TicketUpdate,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    return service.update(ticket_id, payload)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: uuid.UUID,
    service: TicketService = Depends(get_ticket_service),
) -> None:
    service.delete(ticket_id)


@router.post("/{ticket_id}/auto-classify", response_model=ClassificationResult)
def auto_classify_ticket(
    ticket_id: uuid.UUID,
    service: TicketService = Depends(get_ticket_service),
) -> ClassificationResult:
    ticket = service.auto_classify(ticket_id)
    return ticket.classification
