"""FastAPI application entry point for the Banking Transactions API."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.routers import accounts, transactions
from src.utils.errorHandlers import validation_exception_handler

app = FastAPI(
    title="Banking Transactions API",
    description=(
        "RESTful API for managing banking transactions. "
        "Supports creating and querying transactions, filtering by account / type / date range, "
        "retrieving per-account balances, and generating account summaries."
    ),
    version="1.0.0",
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(transactions.router)
app.include_router(accounts.router)
