from .conftest import FIXTURES_DIR


def _upload(client, content: bytes, filename: str = "tickets.csv"):
    return client.post(
        "/tickets/import",
        files={"file": (filename, content, "text/csv")},
    )


def test_valid_csv_imports_all_records(client):
    content = (FIXTURES_DIR / "valid_tickets.csv").read_bytes()

    response = _upload(client, content)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == summary["successful"]
    assert summary["failed"] == 0


def test_mixed_file_reports_invalid_rows_with_error_detail(client):
    header = "customer_id,customer_email,customer_name,subject,description\n"
    valid_row = "CUST-1,jane@example.com,Jane Doe,Cannot log in,I cannot log in to my account since this morning.\n"
    invalid_row = "CUST-2,not-an-email,John Roe,Billing issue,I was charged twice on my last invoice this month.\n"
    content = (header + valid_row + invalid_row).encode("utf-8")

    response = _upload(client, content)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == 2
    assert summary["successful"] == 1
    assert summary["failed"] == 1
    assert len(summary["errors"]) == 1
    assert "customer_email" in summary["errors"][0]["message"]


def test_malformed_csv_structure_returns_400(client):
    header = "customer_id,customer_email,customer_name,subject,description\n"
    row_with_extra_column = (
        "CUST-9,jane@example.com,Jane Doe,Subject,Description that is long enough,extra_value\n"
    )
    content = (header + row_with_extra_column).encode("utf-8")

    response = _upload(client, content)

    assert response.status_code == 400
    assert "detail" in response.json()


def test_empty_file_returns_zero_total(client):
    header_only = b"customer_id,customer_email,customer_name,subject,description\n"

    response = _upload(client, header_only)

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_missing_required_column_reports_per_record_errors(client):
    header = "customer_id,customer_name,subject,description\n"
    row = "CUST-3,Jane Doe,Cannot log in,I cannot log in to my account since this morning.\n"
    content = (header + row).encode("utf-8")

    response = _upload(client, content)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == 1
    assert summary["failed"] == 1
    assert summary["successful"] == 0


def test_auto_classification_applied_to_imported_rows(client):
    content = (FIXTURES_DIR / "valid_tickets.csv").read_bytes()

    response = client.post(
        "/tickets/import?auto_classify=true",
        files={"file": ("tickets.csv", content, "text/csv")},
    )
    summary = response.json()
    ticket_id = summary["created_ticket_ids"][0]

    ticket = client.get(f"/tickets/{ticket_id}").json()
    assert ticket["classification"] is not None
