from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.enums import Category, DeviceType, Priority, Source, Status
from app.models.ticket import Ticket, TicketCreate, TicketMetadata

from .conftest import valid_ticket_payload


def test_valid_ticket_builds_with_all_fields_populated():
    ticket = Ticket(
        **valid_ticket_payload(
            category=Category.account_access,
            priority=Priority.high,
            status=Status.new,
            assigned_to="agent-7",
            tags=["vip", "escalated"],
            metadata=TicketMetadata(
                source=Source.email, browser="Chrome", device_type=DeviceType.mobile
            ),
        )
    )

    assert ticket.customer_id == "CUST-1"
    assert ticket.category == Category.account_access
    assert ticket.priority == Priority.high
    assert ticket.status == Status.new
    assert ticket.assigned_to == "agent-7"
    assert ticket.tags == ["vip", "escalated"]
    assert ticket.metadata.source == Source.email
    assert ticket.metadata.browser == "Chrome"
    assert ticket.metadata.device_type == DeviceType.mobile
    assert ticket.id is not None
    assert ticket.created_at is not None
    assert ticket.updated_at is not None


def test_subject_length_boundaries():
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(subject=""))
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(subject="a" * 201))

    assert TicketCreate(**valid_ticket_payload(subject="a")).subject == "a"
    assert TicketCreate(**valid_ticket_payload(subject="a" * 200)).subject == "a" * 200


def test_description_length_boundaries():
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(description="a" * 9))
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(description="a" * 2001))

    assert TicketCreate(**valid_ticket_payload(description="a" * 10)).description == "a" * 10
    assert (
        TicketCreate(**valid_ticket_payload(description="a" * 2000)).description
        == "a" * 2000
    )


def test_invalid_customer_email_rejected():
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(customer_email="not-an-email"))


def test_invalid_category_enum_rejected():
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(category="not_a_real_category"))


def test_invalid_priority_enum_rejected():
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(priority="super_urgent"))


def test_invalid_status_enum_rejected():
    with pytest.raises(ValidationError):
        TicketCreate(**valid_ticket_payload(status="archived"))


def test_metadata_invalid_source_and_device_type_rejected():
    with pytest.raises(ValidationError):
        TicketMetadata(source="carrier_pigeon")
    with pytest.raises(ValidationError):
        TicketMetadata(device_type="smart_fridge")


def test_defaults_and_nullables():
    ticket = Ticket(**valid_ticket_payload())

    assert ticket.resolved_at is None
    assert ticket.assigned_to is None
    assert ticket.tags == []
    assert ticket.classification is None
    assert isinstance(ticket.created_at, datetime)
    assert isinstance(ticket.updated_at, datetime)
    assert (datetime.now(timezone.utc) - ticket.created_at).total_seconds() < 5
