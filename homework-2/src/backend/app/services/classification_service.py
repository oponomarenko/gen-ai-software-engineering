import logging

from app.classification.engine import classify
from app.models.enums import Category, Priority
from app.models.ticket import ClassificationResult, Ticket

logger = logging.getLogger("classification")


class ClassificationService:
    """Wraps the rule engine and logs every classification decision."""

    def classify_ticket(self, ticket: Ticket) -> ClassificationResult:
        result = classify(ticket.subject, ticket.description)
        logger.info(
            "Auto-classified ticket %s -> category=%s priority=%s confidence=%.2f keywords=%s",
            ticket.id,
            result.category.value,
            result.priority.value,
            result.confidence,
            result.keywords_found,
        )
        return result

    def override(
        self,
        ticket: Ticket,
        category: Category,
        priority: Priority,
        reasoning: str = "Manually overridden by agent.",
    ) -> ClassificationResult:
        result = ClassificationResult(
            category=category,
            priority=priority,
            confidence=1.0,
            reasoning=reasoning,
            keywords_found=[],
            manual_override=True,
        )
        logger.info(
            "Manually overrode classification for ticket %s -> category=%s priority=%s",
            ticket.id,
            category.value,
            priority.value,
        )
        return result


classification_service = ClassificationService()
