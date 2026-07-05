import pytest

from app.classification.engine import classify, classify_category, classify_priority
from app.models.enums import Category, Priority
from app.services.classification_service import ClassificationService

from .conftest import valid_ticket_payload
from app.models.ticket import Ticket


def test_account_access_category_detected():
    text = "login issue: i need to reset password because i am locked out of my account".lower()
    category, confidence, keywords = classify_category(text)
    assert category == Category.account_access
    assert confidence > 0.3
    assert keywords


def test_technical_issue_category_detected():
    text = "the application keeps crashing and is not working properly after the update".lower()
    category, _, keywords = classify_category(text)
    assert category == Category.technical_issue
    assert keywords


def test_billing_question_category_detected():
    text = "i was charged twice on my invoice and would like a refund for the overcharge".lower()
    category, _, keywords = classify_category(text)
    assert category == Category.billing_question
    assert keywords


def test_feature_request_category_detected():
    text = "it would be great if you could add support for exporting reports as csv".lower()
    category, _, keywords = classify_category(text)
    assert category == Category.feature_request
    assert keywords


def test_bug_report_category_detected():
    text = (
        "i found a bug in the checkout flow, steps to reproduce: add an item then "
        "remove it, expected behavior was for the total to update"
    ).lower()
    category, _, keywords = classify_category(text)
    assert category == Category.bug_report
    assert keywords


def test_other_category_is_default_fallback():
    text = "i just wanted to say thanks for the overall experience with the product".lower()
    category, confidence, keywords = classify_category(text)
    assert category == Category.other
    assert confidence == 0.3
    assert keywords == []


@pytest.mark.parametrize(
    "phrase",
    ["can't access", "critical", "production down", "security"],
)
def test_urgent_priority_keywords_detected(phrase):
    text = f"a customer reported that this is {phrase} and needs help right away".lower()
    priority, keywords = classify_priority(text)
    assert priority == Priority.urgent
    assert phrase in keywords


@pytest.mark.parametrize("phrase", ["important", "blocking", "asap"])
def test_high_priority_keywords_detected(phrase):
    text = f"this issue is {phrase} for our team and needs attention soon".lower()
    priority, keywords = classify_priority(text)
    assert priority == Priority.high
    assert phrase in keywords


@pytest.mark.parametrize("phrase", ["minor", "cosmetic", "suggestion"])
def test_low_priority_keywords_detected(phrase):
    text = f"this is just a {phrase} issue with the layout, not a big deal".lower()
    priority, keywords = classify_priority(text)
    assert priority == Priority.low
    assert phrase in keywords


def test_medium_priority_is_default_fallback():
    text = "the dashboard shows the wrong total for last month's report".lower()
    priority, keywords = classify_priority(text)
    assert priority == Priority.medium
    assert keywords == []


def test_classification_result_is_complete_and_manual_override_preserved():
    result = classify(
        subject="Login issue",
        description="I forgot my password and am locked out of my account, this is critical.",
    )

    assert 0.0 <= result.confidence <= 1.0
    assert result.reasoning
    assert result.category == Category.account_access
    assert result.priority == Priority.urgent
    assert "locked out" in result.keywords_found
    assert "critical" in result.keywords_found
    assert result.manual_override is False

    ticket = Ticket(**valid_ticket_payload())
    override = ClassificationService().override(
        ticket=ticket,
        category=Category.billing_question,
        priority=Priority.high,
    )
    assert override.manual_override is True
    assert override.confidence == 1.0
