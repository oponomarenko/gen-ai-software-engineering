"""FastAPI application entry point for the Banking Transactions API."""

from fastapi import FastAPI

from src.routers import accounts, transactions

app = FastAPI(title="Banking Transactions API")

app.include_router(transactions.router)
app.include_router(accounts.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker and local smoke tests."""
    return {"status": "ok"}
