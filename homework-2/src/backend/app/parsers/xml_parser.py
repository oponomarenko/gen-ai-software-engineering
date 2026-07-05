from typing import Any

from defusedxml import ElementTree as SafeET
from defusedxml.common import DefusedXmlException
from xml.etree.ElementTree import ParseError as ElementTreeParseError

from app.parsers.base import ParseError, TicketParser

_LIST_FIELDS = {"tags"}


def _element_to_value(el) -> Any:
    children = list(el)
    if not children:
        if el.tag in _LIST_FIELDS:
            return []
        text = (el.text or "").strip()
        return text if text != "" else None

    if el.tag in _LIST_FIELDS or all(child.tag == children[0].tag for child in children):
        return [_element_to_value(child) for child in children]

    return {child.tag: _element_to_value(child) for child in children}


class XmlTicketParser(TicketParser):
    def parse(self, content: bytes) -> list[dict[str, Any]]:
        try:
            root = SafeET.fromstring(content)
        except (ElementTreeParseError, DefusedXmlException) as exc:
            raise ParseError(f"Invalid XML: {exc}") from exc

        if root.tag == "ticket":
            ticket_elements = [root]
        else:
            ticket_elements = root.findall("ticket")

        records: list[dict[str, Any]] = []
        for ticket_el in ticket_elements:
            record: dict[str, Any] = {}
            for child in ticket_el:
                record[child.tag] = _element_to_value(child)
            records.append(record)
        return records
