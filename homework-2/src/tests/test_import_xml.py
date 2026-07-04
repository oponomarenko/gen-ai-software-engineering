from .conftest import FIXTURES_DIR


def _upload(client, content: bytes, filename: str = "tickets.xml"):
    return client.post(
        "/tickets/import",
        files={"file": (filename, content, "application/xml")},
    )


def test_valid_xml_imports_all_successfully(client):
    content = (FIXTURES_DIR / "valid_tickets.xml").read_bytes()

    response = _upload(client, content)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == 3
    assert summary["successful"] == 3
    assert summary["failed"] == 0


def test_malformed_xml_returns_400(client):
    content = (FIXTURES_DIR / "malformed.xml").read_bytes()

    response = _upload(client, content)

    assert response.status_code == 400
    assert "detail" in response.json()


def test_per_record_validation_errors_reported(client):
    content = (FIXTURES_DIR / "invalid_enum.xml").read_bytes()

    response = _upload(client, content)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == 1
    assert summary["failed"] == 1
    assert summary["successful"] == 0


def test_xxe_payload_is_neutralized(client):
    content = b"""<?xml version="1.0"?>
<!DOCTYPE tickets [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<tickets>
  <ticket>
    <customer_id>&xxe;</customer_id>
    <customer_email>test@example.com</customer_email>
    <customer_name>Attacker</customer_name>
    <subject>XXE probe</subject>
    <description>This description tries to trigger an XXE via external entity.</description>
  </ticket>
</tickets>
"""

    response = _upload(client, content)

    assert response.status_code == 400
    body = response.json()
    assert "root:" not in body["detail"]


def test_empty_document_returns_zero_total(client):
    content = b"<tickets></tickets>"

    response = _upload(client, content)

    assert response.status_code == 200
    assert response.json()["total"] == 0
