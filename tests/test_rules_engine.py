# tests/test_rules_engine.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from utils.rules_engine import (
    evaluate_string,
    evaluate_date,
    evaluate_condition,
    evaluate_rule,
    apply_actions,
)


@pytest.mark.parametrize(
    "predicate,value,expected",
    [
        ("contains", "hello", True),
        ("contains", "WORLD", True),
        ("does not contain", "xyz", True),
        ("equals", "Hello World", True),
        ("does not equal", "Hello", True),
    ],
)
def test_evaluate_string(predicate, value, expected):
    assert evaluate_string("Hello World", predicate, value) == expected


def test_evaluate_string_unknown_predicate():
    with pytest.raises(ValueError):
        evaluate_string("test", "unknown", "x")


def test_evaluate_date_less_than():
    past_date = (datetime.now() - timedelta(days=5)).strftime("%a, %d %b %Y %H:%M:%S") # noqa
    assert evaluate_date(past_date, "less than", 10) is True


def test_evaluate_date_greater_than():
    past_date = (datetime.now() - timedelta(days=20)).strftime("%a, %d %b %Y %H:%M:%S") # noqa
    assert evaluate_date(past_date, "greater than", 10) is True


def test_evaluate_date_bad_format():
    assert evaluate_date("bad date", "less than", 5) is False


def test_evaluate_date_unknown_predicate():
    date_str = (datetime.now() - timedelta(days=5)).strftime("%a, %d %b %Y %H:%M:%S") # noqa
    with pytest.raises(ValueError):
        evaluate_date(date_str, "unknown", 5)


EMAIL = {
    "from_email": "alice@example.com",
    "to_email": "bob@example.com",
    "subject": "Hello World",
    "snippet": "This is a test email",
    "date": (datetime.now() - timedelta(days=2)).strftime("%a, %d %b %Y %H:%M:%S"), # noqa
}


def test_evaluate_condition_subject_contains():
    condition = {"field": "subject", "predicate": "contains", "value": "Hello"}
    assert evaluate_condition(EMAIL, condition) is True


def test_evaluate_condition_unknown_field():
    condition = {"field": "foo", "predicate": "contains", "value": "x"}
    with pytest.raises(ValueError):
        evaluate_condition(EMAIL, condition)


def test_evaluate_rule_all_true():
    rule = {
        "conditions_predicate": "All",
        "conditions": [
            {"field": "subject", "predicate": "contains", "value": "Hello"},
            {"field": "snippet", "predicate": "contains", "value": "test"},
        ],
    }
    assert evaluate_rule(EMAIL, rule) is True


def test_evaluate_rule_any_true():
    rule = {
        "conditions_predicate": "Any",
        "conditions": [
            {"field": "subject", "predicate": "contains", "value": "Hello"},
            {"field": "snippet", "predicate": "contains", "value": "absent"},
        ],
    }
    assert evaluate_rule(EMAIL, rule) is True


def test_evaluate_rule_all_false():
    rule = {
        "conditions_predicate": "All",
        "conditions": [
            {"field": "subject", "predicate": "contains", "value": "missing"},
            {"field": "snippet", "predicate": "contains", "value": "absent"},
        ],
    }
    assert evaluate_rule(EMAIL, rule) is False


def test_evaluate_rule_unknown_overall_predicate():
    rule = {"conditions_predicate": "SomethingElse", "conditions": []}
    with pytest.raises(ValueError):
        evaluate_rule(EMAIL, rule)


@pytest.fixture
def mock_service():
    service = Mock()
    service.users.return_value.messages.return_value.modify.return_value.execute.return_value = ( # noqa 
        {}
    )
    service.users.return_value.labels.return_value.list.return_value.execute.return_value = {  # noqa
        "labels": []
    }
    service.users.return_value.labels.return_value.create.return_value.execute.return_value = { # noqa
        "id": "new_label_id"
    }
    return service


def test_apply_actions_mark_as_read(mock_service):
    email = {"id": "123"}
    apply_actions(email, ["mark_as_read"], mock_service)
    mock_service.users().messages().modify.assert_called_with(
        userId="me", id="123", body={"removeLabelIds": ["UNREAD"]}
    )


def test_apply_actions_mark_as_unread(mock_service):
    email = {"id": "123"}
    apply_actions(email, ["mark_as_unread"], mock_service)
    mock_service.users().messages().modify.assert_called_with(
        userId="me", id="123", body={"addLabelIds": ["UNREAD"]}
    )


@patch("utils.rules_engine.get_label_id", return_value="new_label_id")
def test_apply_actions_move_to_label_creates_label(
    mock_get_label_id, mock_service
):  # noqa
    email = {"id": "123"}
    apply_actions(email, ["move_to:Important"], mock_service)
    mock_get_label_id.assert_called_with(mock_service, "Important")
    mock_service.users().messages().modify.assert_called_with(
        userId="me", id="123", body={"addLabelIds": ["new_label_id"]}
    )
