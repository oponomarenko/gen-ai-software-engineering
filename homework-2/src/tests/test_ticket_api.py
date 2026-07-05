import uuid

from .conftest import valid_ticket_payload


def test_create_ticket_returns_201_with_id_and_timestamps(client):
    response = client.post("/tickets", json=valid_ticket_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_ticket_with_auto_classify_populates_classification(client):
    response = client.post(
        "/tickets?auto_classify=true",
        json=valid_ticket_payload(
            subject="Cannot log in",
            description="I forgot my password and am locked out of my account.",
        ),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["classification"] is not None
    assert body["classification"]["category"]
    assert body["classification"]["priority"]


def test_create_ticket_invalid_payload_returns_422(client):
    payload = valid_ticket_payload(customer_email="not-an-email")

    response = client.post("/tickets", json=payload)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_list_tickets_returns_all(client):
    client.post("/tickets", json=valid_ticket_payload(customer_id="CUST-A"))
    client.post("/tickets", json=valid_ticket_payload(customer_id="CUST-B"))

    response = client.get("/tickets")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tickets_filters_by_category(client):
    client.post("/tickets", json=valid_ticket_payload(category="billing_question"))
    client.post("/tickets", json=valid_ticket_payload(category="bug_report"))

    response = client.get("/tickets", params={"category": "billing_question"})

    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["category"] == "billing_question"


def test_list_tickets_filters_by_priority(client):
    client.post("/tickets", json=valid_ticket_payload(priority="urgent"))
    client.post("/tickets", json=valid_ticket_payload(priority="low"))

    response = client.get("/tickets", params={"priority": "urgent"})

    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["priority"] == "urgent"


def test_list_tickets_filters_by_status(client):
    client.post("/tickets", json=valid_ticket_payload(status="resolved"))
    client.post("/tickets", json=valid_ticket_payload(status="new"))

    response = client.get("/tickets", params={"status": "resolved"})

    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["status"] == "resolved"


def test_get_ticket_by_id_returns_200(client):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.get(f"/tickets/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_ticket_unknown_id_returns_404(client):
    response = client.get(f"/tickets/{uuid.uuid4()}")

    assert response.status_code == 404


def test_update_ticket_returns_200_and_unknown_id_returns_404(client):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.put(f"/tickets/{created['id']}", json={"subject": "Updated subject"})

    assert response.status_code == 200
    assert response.json()["subject"] == "Updated subject"

    missing_response = client.put(f"/tickets/{uuid.uuid4()}", json={"subject": "Nope"})
    assert missing_response.status_code == 404


def test_delete_ticket_returns_204_and_unknown_id_returns_404(client):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.delete(f"/tickets/{created['id']}")
    assert response.status_code == 204

    missing_response = client.delete(f"/tickets/{created['id']}")
    assert missing_response.status_code == 404
