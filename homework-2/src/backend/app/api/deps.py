from functools import lru_cache

from app.parsers.csv_parser import CsvTicketParser
from app.parsers.json_parser import JsonTicketParser
from app.parsers.xml_parser import XmlTicketParser
from app.repository.memory import InMemoryTicketRepository
from app.services.classification_service import ClassificationService
from app.services.import_service import ImportService
from app.services.ticket_service import TicketService


@lru_cache
def get_repository() -> InMemoryTicketRepository:
    return InMemoryTicketRepository()


@lru_cache
def get_classification_service() -> ClassificationService:
    return ClassificationService()


@lru_cache
def get_ticket_service() -> TicketService:
    return TicketService(get_repository(), get_classification_service())


@lru_cache
def get_import_service() -> ImportService:
    return ImportService(
        repository=get_repository(),
        classification_service=get_classification_service(),
        parsers={
            "csv": CsvTicketParser(),
            "json": JsonTicketParser(),
            "xml": XmlTicketParser(),
        },
    )
