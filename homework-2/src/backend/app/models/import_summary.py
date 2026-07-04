from pydantic import BaseModel


class ImportRecordError(BaseModel):
    record_index: int
    identifier: str | None = None
    message: str


class ImportSummary(BaseModel):
    total: int
    successful: int
    failed: int
    errors: list[ImportRecordError] = []
    created_ticket_ids: list[str] = []
