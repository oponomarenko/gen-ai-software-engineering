from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str):
        self.message = message


class BadRequestError(Exception):
    """Raised for semantic validation failures that aren't caught by Pydantic."""

    def __init__(self, message: str):
        self.message = message


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


async def bad_request_handler(request: Request, exc: BadRequestError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.message})
