# tests/test_process_emails.py
import json
import pytest
from unittest.mock import Mock, patch, mock_open
from rule_processor import RuleProcessor
from .data_store import EMAILS, RULES_JSON


@pytest.fixture
def mock_service():
    return Mock()


@pytest.fixture
def mock_email_db():
    db = Mock()
    db.get_emails.return_value = EMAILS
    return db


@pytest.fixture
def mock_logger():
    return Mock()


@patch(
    "builtins.open", new_callable=mock_open, read_data=json.dumps(RULES_JSON)
)  # noqa
@patch("rule_processor.rules_engine.evaluate_rule", return_value=True)
@patch("rule_processor.rules_engine.apply_actions")
def test_process_emails(
    mock_apply, mock_eval, mock_file, mock_email_db, mock_service, mock_logger
):
    processor = RuleProcessor(
        email_db=mock_email_db,
        service=mock_service,
        rules_file_path="rules.json",
        logger=mock_logger,
    )
    processor.load_rules()
    processor.process_emails()

    # rules.json read
    mock_file.assert_called_with("rules.json", "r")

    # Emails fetched
    mock_email_db.get_emails.assert_called_once()

    # evaluate_rule called for each email x each rule
    assert mock_eval.call_count == len(EMAILS) * len(RULES_JSON)

    # apply_actions called the same number of times
    assert mock_apply.call_count == len(EMAILS) * len(RULES_JSON)


@patch("builtins.open", side_effect=FileNotFoundError)
def test_no_rules_file(mock_file, mock_email_db, mock_service, mock_logger):
    processor = RuleProcessor(
        email_db=mock_email_db,
        service=mock_service,
        rules_file_path="rules.json",
        logger=mock_logger,
    )
    processor.load_rules()
    processor.process_emails()
    mock_file.assert_called_once_with("rules.json", "r")


@patch("builtins.open", new_callable=mock_open, read_data="[]")
def test_empty_rules(mock_file, mock_email_db, mock_service, mock_logger):
    processor = RuleProcessor(
        email_db=mock_email_db,
        service=mock_service,
        rules_file_path="rules.json",
        logger=mock_logger,
    )
    processor.load_rules()
    processor.process_emails()
    mock_file.assert_called_once_with("rules.json", "r")


@patch(
    "builtins.open", new_callable=mock_open, read_data=json.dumps(RULES_JSON)
)  # noqa
def test_no_emails(mock_file, mock_email_db, mock_service, mock_logger):
    mock_email_db.get_emails.return_value = []
    processor = RuleProcessor(
        email_db=mock_email_db,
        service=mock_service,
        rules_file_path="rules.json",
        logger=mock_logger,
    )
    processor.load_rules()
    processor.process_emails()
    mock_email_db.get_emails.assert_called_once()


@patch(
    "builtins.open", new_callable=mock_open, read_data=json.dumps(RULES_JSON)
)  # noqa
@patch(
    "rule_processor.rules_engine.evaluate_rule",
    side_effect=Exception("Test error"),  # noqa
)
@patch("rule_processor.rules_engine.apply_actions")
def test_evaluate_rule_exception(
    mock_apply, mock_eval, mock_file, mock_email_db, mock_service, mock_logger
):
    processor = RuleProcessor(
        email_db=mock_email_db,
        service=mock_service,
        rules_file_path="rules.json",
        logger=mock_logger,
    )
    processor.load_rules()
    processor.process_emails()

    # Even though evaluate_rule raises, apply_actions should never be called
    mock_apply.assert_not_called()

    # evaluate_rule should still be called for each email x each rule
    assert mock_eval.call_count == len(EMAILS) * len(RULES_JSON)


@patch(
    "builtins.open", new_callable=mock_open, read_data=json.dumps(RULES_JSON)
)  # noqa
@patch("rule_processor.rules_engine.evaluate_rule", return_value=True)
@patch(
    "rule_processor.rules_engine.apply_actions",
    side_effect=Exception("Action error"),  # noqa
)
def test_apply_actions_exception(
    mock_apply, mock_eval, mock_file, mock_email_db, mock_service, mock_logger
):
    processor = RuleProcessor(
        email_db=mock_email_db,
        service=mock_service,
        rules_file_path="rules.json",
        logger=mock_logger,
    )
    processor.load_rules()
    processor.process_emails()

    # evaluate_rule should be called for each email x each rule
    assert mock_eval.call_count == len(EMAILS) * len(RULES_JSON)

    assert mock_apply.call_count == len(EMAILS) * len(RULES_JSON)
