from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api import deps
from app.main import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _reset_repository():
    deps.get_repository().clear()
    yield
    deps.get_repository().clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def valid_ticket_payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "customer_id": "CUST-1",
        "customer_email": "jane.doe@example.com",
        "customer_name": "Jane Doe",
        "subject": "Cannot log in to my account",
        "description": "I have been unable to log in since this morning despite resetting my password.",
    }
    payload.update(overrides)
    return payload
