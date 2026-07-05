from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, tickets
from app.core.config import settings
from app.core.errors import BadRequestError, NotFoundError, bad_request_handler, not_found_handler

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(BadRequestError, bad_request_handler)

app.include_router(health.router)
app.include_router(tickets.router)
