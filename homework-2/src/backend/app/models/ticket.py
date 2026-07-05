import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Category, DeviceType, Priority, Source, Status


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TicketMetadata(BaseModel):
    source: Source = Source.web_form
    browser: str | None = None
    device_type: DeviceType | None = None


class ClassificationResult(BaseModel):
    category: Category
    priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    keywords_found: list[str] = Field(default_factory=list)
    manual_override: bool = False


class TicketBase(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    customer_email: EmailStr
    customer_name: str = Field(min_length=1, max_length=200)
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    category: Category = Category.other
    priority: Priority = Priority.medium
    status: Status = Status.new
    assigned_to: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: TicketMetadata = Field(default_factory=TicketMetadata)


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    customer_id: str | None = Field(default=None, min_length=1, max_length=100)
    customer_email: EmailStr | None = None
    customer_name: str | None = Field(default=None, min_length=1, max_length=200)
    subject: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=10, max_length=2000)
    category: Category | None = None
    priority: Priority | None = None
    status: Status | None = None
    assigned_to: str | None = None
    tags: list[str] | None = None
    metadata: TicketMetadata | None = None


class Ticket(TicketBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    resolved_at: datetime | None = None
    classification: ClassificationResult | None = None
