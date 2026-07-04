import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.classification.engine import classify

from .conftest import valid_ticket_payload

SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent / "sample_data"


def test_full_ticket_lifecycle(client):
    created = client.post("/tickets", json=valid_ticket_payload()).json()
    ticket_id = created["id"]
    assert created["status"] == "new"

    classified = client.post(f"/tickets/{ticket_id}/auto-classify")
    assert classified.status_code == 200
    assert classified.json()["category"]

    in_progress = client.put(f"/tickets/{ticket_id}", json={"status": "in_progress"})
    assert in_progress.status_code == 200
    assert in_progress.json()["status"] == "in_progress"
    assert in_progress.json()["resolved_at"] is None

    resolved = client.put(f"/tickets/{ticket_id}", json={"status": "resolved"})
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"
    assert resolved.json()["resolved_at"] is not None

    deleted = client.delete(f"/tickets/{ticket_id}")
    assert deleted.status_code == 204
    assert client.get(f"/tickets/{ticket_id}").status_code == 404


def test_bulk_import_and_auto_classify_verification(client):
    content = (SAMPLE_DATA_DIR / "sample_tickets.csv").read_bytes()

    response = client.post(
        "/tickets/import?auto_classify=true",
        files={"file": ("sample_tickets.csv", content, "text/csv")},
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == 50
    assert summary["successful"] == 50
    assert summary["failed"] == 0

    for ticket_id in summary["created_ticket_ids"]:
        ticket = client.get(f"/tickets/{ticket_id}").json()
        assert ticket["classification"] is not None
        expected = classify(ticket["subject"], ticket["description"])
        assert ticket["category"] == expected.category.value
        assert ticket["priority"] == expected.priority.value


def test_concurrent_operations_stay_consistent(client):
    def create(index: int):
        return client.post("/tickets", json=valid_ticket_payload(customer_id=f"CUST-{index}"))

    with ThreadPoolExecutor(max_workers=20) as executor:
        responses = list(executor.map(create, range(20)))

    assert all(r.status_code == 201 for r in responses)
    ids = [r.json()["id"] for r in responses]
    assert len(set(ids)) == 20

    def read(_: int):
        return client.get("/tickets")

    with ThreadPoolExecutor(max_workers=20) as executor:
        read_responses = list(executor.map(read, range(20)))

    assert all(r.status_code == 200 for r in read_responses)
    assert all(len(r.json()) == 20 for r in read_responses)


def test_combined_filtering_matches_both_criteria(client):
    client.post(
        "/tickets", json=valid_ticket_payload(category="billing_question", priority="urgent")
    )
    client.post(
        "/tickets", json=valid_ticket_payload(category="billing_question", priority="low")
    )
    client.post("/tickets", json=valid_ticket_payload(category="bug_report", priority="urgent"))

    response = client.get("/tickets", params={"category": "billing_question", "priority": "urgent"})

    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["category"] == "billing_question"
    assert tickets[0]["priority"] == "urgent"


def test_manual_override_persists_and_is_not_recomputed(client):
    created = client.post(
        "/tickets?auto_classify=true",
        json=valid_ticket_payload(
            subject="Cannot log in",
            description="I forgot my password and am locked out of my account.",
        ),
    ).json()
    ticket_id = created["id"]
    assert created["category"] == "account_access"

    overridden = client.put(
        f"/tickets/{ticket_id}", json={"category": "billing_question", "priority": "high"}
    )
    assert overridden.status_code == 200
    body = overridden.json()
    assert body["category"] == "billing_question"
    assert body["priority"] == "high"
    assert body["classification"]["manual_override"] is True

    refetched = client.get(f"/tickets/{ticket_id}").json()
    assert refetched["category"] == "billing_question"
    assert refetched["priority"] == "high"
    assert refetched["classification"]["manual_override"] is True
