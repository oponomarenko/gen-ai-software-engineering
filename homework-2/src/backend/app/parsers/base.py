from abc import ABC, abstractmethod
from typing import Any


class ParseError(Exception):
    """Raised when a file cannot be parsed at all (malformed structure)."""


class TicketParser(ABC):
    """Converts raw file bytes into a list of candidate ticket dicts.

    Implementations must never raise for a single bad record — record-level
    problems are surfaced later during Pydantic validation in ImportService.
    Only structurally malformed files raise ParseError.
    """

    @abstractmethod
    def parse(self, content: bytes) -> list[dict[str, Any]]: ...
