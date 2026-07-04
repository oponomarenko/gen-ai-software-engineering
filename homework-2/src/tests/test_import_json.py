from .conftest import FIXTURES_DIR


def _upload(client, content: bytes, filename: str = "tickets.json"):
    return client.post(
        "/tickets/import",
        files={"file": (filename, content, "application/json")},
    )


def test_valid_json_array_imports_all_successfully(client):
    content = (FIXTURES_DIR / "valid_tickets.json").read_bytes()

    response = _upload(client, content)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == 3
    assert summary["successful"] == 3
    assert summary["failed"] == 0


def test_invalid_json_syntax_returns_400(client):
    content = (FIXTURES_DIR / "malformed.json").read_bytes()

    response = _upload(client, content)

    assert response.status_code == 400
    assert "detail" in response.json()


def test_per_record_validation_errors_reported(client):
    content = (FIXTURES_DIR / "invalid_short_description.json").read_bytes()

    response = _upload(client, content)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total"] == 1
    assert summary["failed"] == 1
    assert summary["successful"] == 0
    assert "description" in summary["errors"][0]["message"]


def test_wrong_shape_returns_400(client):
    content = b'"just a plain string, not a ticket list"'

    response = _upload(client, content)

    assert response.status_code == 400
    assert "detail" in response.json()


def test_empty_array_returns_zero_total(client):
    content = b"[]"

    response = _upload(client, content)

    assert response.status_code == 200
    assert response.json()["total"] == 0
