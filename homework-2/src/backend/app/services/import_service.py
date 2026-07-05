from typing import Any

from pydantic import ValidationError

from app.core.errors import BadRequestError
from app.models.import_summary import ImportRecordError, ImportSummary
from app.models.ticket import Ticket, TicketCreate
from app.parsers.base import ParseError, TicketParser
from app.repository.base import TicketRepository
from app.services.classification_service import ClassificationService


class ImportService:
    def __init__(
        self,
        repository: TicketRepository,
        classification_service: ClassificationService,
        parsers: dict[str, TicketParser],
    ):
        self._repository = repository
        self._classification_service = classification_service
        self._parsers = parsers

    def resolve_format(self, filename: str | None, content_type: str | None) -> str:
        if filename and "." in filename:
            ext = filename.rsplit(".", 1)[-1].lower()
            if ext in self._parsers:
                return ext
        if content_type:
            for fmt in self._parsers:
                if fmt in content_type.lower():
                    return fmt
        raise BadRequestError(
            "Unable to determine import format; use a .csv, .json, or .xml filename."
        )

    def import_file(
        self,
        content: bytes,
        filename: str | None,
        content_type: str | None,
        auto_classify: bool = True,
    ) -> ImportSummary:
        fmt = self.resolve_format(filename, content_type)
        parser = self._parsers[fmt]

        try:
            records = parser.parse(content)
        except ParseError as exc:
            raise BadRequestError(f"Malformed {fmt.upper()} file: {exc}") from exc

        errors: list[ImportRecordError] = []
        created_ids: list[str] = []

        for index, record in enumerate(records):
            identifier = str(record.get("customer_id") or record.get("subject") or "")
            try:
                payload = TicketCreate.model_validate(record)
            except ValidationError as exc:
                errors.append(
                    ImportRecordError(
                        record_index=index,
                        identifier=identifier or None,
                        message="; ".join(
                            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                            for err in exc.errors()
                        ),
                    )
                )
                continue

            ticket = Ticket(**payload.model_dump())
            if auto_classify:
                result = self._classification_service.classify_ticket(ticket)
                ticket.classification = result
                ticket.category = result.category
                ticket.priority = result.priority

            self._repository.create(ticket)
            created_ids.append(str(ticket.id))

        return ImportSummary(
            total=len(records),
            successful=len(created_ids),
            failed=len(errors),
            errors=errors,
            created_ticket_ids=created_ids,
        )
