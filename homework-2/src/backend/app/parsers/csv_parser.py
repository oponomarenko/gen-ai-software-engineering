import csv
import io
from typing import Any

from app.parsers.base import ParseError, TicketParser

_LIST_FIELDS = {"tags"}
_NESTED_METADATA_PREFIX = "metadata."


def _coerce_value(key: str, value: str) -> Any:
    value = value.strip()
    if key in _LIST_FIELDS:
        return [v.strip() for v in value.split("|") if v.strip()] if value else []
    return value if value != "" else None


class CsvTicketParser(TicketParser):
    def parse(self, content: bytes) -> list[dict[str, Any]]:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ParseError(f"Invalid encoding: {exc}") from exc

        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames is None:
            raise ParseError("CSV file has no header row")

        records: list[dict[str, Any]] = []
        for row in reader:
            if None in row:
                raise ParseError("CSV row has more columns than header")
            record: dict[str, Any] = {}
            metadata: dict[str, Any] = {}
            for key, raw_value in row.items():
                value = _coerce_value(key, raw_value or "")
                if key.startswith(_NESTED_METADATA_PREFIX):
                    metadata[key[len(_NESTED_METADATA_PREFIX):]] = value
                else:
                    record[key] = value
            if metadata:
                record["metadata"] = {k: v for k, v in metadata.items() if v is not None}
            records.append(record)
        return records
