"""FastAPI application entry point for the Banking Transactions API."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.routers import accounts, transactions
from src.utils.errorHandlers import validation_exception_handler

app = FastAPI(title="Banking Transactions API")

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(transactions.router)
app.include_router(accounts.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker and local smoke tests."""
    return {"status": "ok"}
