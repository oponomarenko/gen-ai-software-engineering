from app.classification.keywords import CATEGORY_KEYWORDS, PRIORITY_KEYWORDS
from app.models.enums import Category, Priority
from app.models.ticket import ClassificationResult

_PRIORITY_ORDER = [Priority.urgent, Priority.high, Priority.low]


def _find_keywords(text: str, keywords: list[str]) -> list[str]:
    return [kw for kw in keywords if kw in text]


def classify_category(text: str) -> tuple[Category, float, list[str]]:
    best_category = Category.other
    best_keywords: list[str] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = _find_keywords(text, keywords)
        if len(matched) > len(best_keywords):
            best_category = category
            best_keywords = matched

    if not best_keywords:
        return Category.other, 0.3, []

    confidence = min(1.0, 0.5 + 0.15 * len(best_keywords))
    return best_category, confidence, best_keywords


def classify_priority(text: str) -> tuple[Priority, list[str]]:
    for priority in _PRIORITY_ORDER:
        matched = _find_keywords(text, PRIORITY_KEYWORDS[priority])
        if matched:
            return priority, matched
    return Priority.medium, []


def classify(subject: str, description: str) -> ClassificationResult:
    text = f"{subject} {description}".lower()

    category, confidence, category_keywords = classify_category(text)
    priority, priority_keywords = classify_priority(text)

    keywords_found = category_keywords + priority_keywords

    if category_keywords:
        category_reason = (
            f"Matched category keyword(s) {category_keywords} -> '{category.value}'."
        )
    else:
        category_reason = "No category keywords matched; defaulted to 'other'."

    if priority_keywords:
        priority_reason = (
            f"Matched priority keyword(s) {priority_keywords} -> '{priority.value}'."
        )
    else:
        priority_reason = "No priority keywords matched; defaulted to 'medium'."

    reasoning = f"{category_reason} {priority_reason}"

    return ClassificationResult(
        category=category,
        priority=priority,
        confidence=confidence,
        reasoning=reasoning,
        keywords_found=keywords_found,
        manual_override=False,
    )
