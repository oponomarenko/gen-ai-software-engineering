"""FastAPI application entry point for the Banking Transactions API."""

from fastapi import FastAPI

app = FastAPI(title="Banking Transactions API")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker and local smoke tests."""
    return {"status": "ok"}
