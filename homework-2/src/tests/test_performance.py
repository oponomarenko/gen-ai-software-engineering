import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .conftest import valid_ticket_payload

SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent / "sample_data"

SINGLE_CREATE_BUDGET_SECONDS = 0.5
LIST_BUDGET_SECONDS = 1.0
BULK_IMPORT_BUDGET_SECONDS = 3.0
AUTO_CLASSIFY_BUDGET_SECONDS = 0.5
CONCURRENT_BUDGET_SECONDS = 5.0


def test_single_create_latency_under_budget(client):
    start = time.perf_counter()
    response = client.post("/tickets", json=valid_ticket_payload())
    elapsed = time.perf_counter() - start

    assert response.status_code == 201
    assert elapsed < SINGLE_CREATE_BUDGET_SECONDS


def test_list_latency_over_seeded_dataset_under_budget(client):
    for i in range(100):
        client.post("/tickets", json=valid_ticket_payload(customer_id=f"CUST-{i}"))

    start = time.perf_counter()
    response = client.get("/tickets")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert len(response.json()) == 100
    assert elapsed < LIST_BUDGET_SECONDS


def test_bulk_import_throughput_under_budget(client):
    content = (SAMPLE_DATA_DIR / "sample_tickets.csv").read_bytes()

    start = time.perf_counter()
    response = client.post(
        "/tickets/import?auto_classify=true",
        files={"file": ("sample_tickets.csv", content, "text/csv")},
    )
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert response.json()["successful"] == 50
    assert elapsed < BULK_IMPORT_BUDGET_SECONDS


def test_auto_classify_latency_under_budget(client):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    start = time.perf_counter()
    response = client.post(f"/tickets/{created['id']}/auto-classify")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < AUTO_CLASSIFY_BUDGET_SECONDS


def test_concurrent_throughput_under_budget(client):
    def create(index: int):
        return client.post("/tickets", json=valid_ticket_payload(customer_id=f"CUST-{index}"))

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=20) as executor:
        responses = list(executor.map(create, range(20)))
    elapsed = time.perf_counter() - start

    assert all(r.status_code == 201 for r in responses)
    assert elapsed < CONCURRENT_BUDGET_SECONDS
