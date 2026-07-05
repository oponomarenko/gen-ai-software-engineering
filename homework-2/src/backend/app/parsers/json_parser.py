import json
from typing import Any

from app.parsers.base import ParseError, TicketParser


class JsonTicketParser(TicketParser):
    def parse(self, content: bytes) -> list[dict[str, Any]]:
        try:
            data = json.loads(content.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ParseError(f"Invalid encoding: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ParseError(f"Invalid JSON: {exc}") from exc

        if isinstance(data, dict):
            if "tickets" in data and isinstance(data["tickets"], list):
                data = data["tickets"]
            else:
                data = [data]

        if not isinstance(data, list):
            raise ParseError("JSON payload must be an object, a ticket list, or {'tickets': [...]}")

        for i, record in enumerate(data):
            if not isinstance(record, dict):
                raise ParseError(f"Record at index {i} is not a JSON object")

        return data
