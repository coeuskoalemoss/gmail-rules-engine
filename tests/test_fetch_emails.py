# tests/test_fetch_emails.py
import pytest
from unittest.mock import Mock
from googleapiclient.errors import HttpError
from gmail_utils.gmail_email_fetcher import GmailEmailFetcher


@pytest.fixture
def mock_service():
    return Mock()


@pytest.fixture
def mock_email_db():
    return Mock()


@pytest.fixture
def mock_logger():
    return Mock()


def test_fetch_and_save_emails(mock_service, mock_email_db, mock_logger):
    # Mock list().execute() to return 2 messages
    mock_service.users().messages().list().execute.return_value = {
        "messages": [{"id": "1"}, {"id": "2"}]
    }

    # Mock get().execute() to return full message details
    mock_service.users().messages().get().execute.side_effect = [
        {
            "id": "1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "alice@example.com"},
                    {"name": "To", "value": "me@example.com"},
                    {"name": "Subject", "value": "Hello"},
                    {
                        "name": "Date",
                        "value": "Fri, 26 Sep 2025 12:00:00 -0700",
                    },  # noqa
                ]
            },
            "snippet": "Hello snippet",
        },
        {
            "id": "2",
            "payload": {
                "headers": [
                    {"name": "From", "value": "bob@example.com"},
                    {"name": "To", "value": "me@example.com"},
                    {"name": "Subject", "value": "World"},
                    {
                        "name": "Date",
                        "value": "Fri, 26 Sep 2025 12:00:00 -0700",
                    },  # noqa
                ]
            },
            "snippet": "World snippet",
        },
    ]

    fetcher = GmailEmailFetcher(
        service=mock_service, email_db=mock_email_db, logger=mock_logger
    )
    fetcher.fetch_and_save_emails()

    # db.save_email called twice
    assert mock_email_db.save_email.call_count == 2
    # Check first call data
    first_call_args = mock_email_db.save_email.call_args_list[0][1]["email"]
    assert first_call_args["subject"] == "Hello"
    assert first_call_args["from_email"] == "alice@example.com"


def test_no_messages(mock_service, mock_email_db, mock_logger):
    mock_service.users().messages().list().execute.return_value = {"messages": []} # noqa
    fetcher = GmailEmailFetcher(
        service=mock_service, email_db=mock_email_db, logger=mock_logger
    )
    fetcher.fetch_and_save_emails()
    # db.save_email should never be called
    mock_email_db.save_email.assert_not_called()


def test_http_error(mock_service, mock_email_db, mock_logger):
    # Simulate HttpError on list()
    mock_service.users().messages().list().execute.side_effect = HttpError(
        resp=Mock(status=500), content=b"Server Error"
    )
    fetcher = GmailEmailFetcher(
        service=mock_service, email_db=mock_email_db, logger=mock_logger
    )
    fetcher.fetch_and_save_emails()
    mock_email_db.save_email.assert_not_called()
