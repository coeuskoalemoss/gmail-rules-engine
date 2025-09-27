import pytest
from database.email_database import EmailDatabase
from unittest.mock import Mock
import sqlite3

TEST_EMAIL = {
    "id": "12345",
    "from_email": "sender@example.com",
    "to_email": "me@example.com",
    "subject": "Test email",
    "date": "2025-09-25",
    "snippet": "This is a test snippet",
}


@pytest.fixture
def db_instance(tmp_path):
    """Fixture to use a fresh test DB for each test."""
    db_file = tmp_path / "test_emails.db"
    mock_logger = Mock()
    db = EmailDatabase(db_name=str(db_file), logger=mock_logger)
    yield db


def test_init_db_creates_table(db_instance):
    conn = sqlite3.connect(db_instance.db_name)
    c = conn.cursor()
    c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='emails'"
    )  # noqa
    result = c.fetchone()
    conn.close()
    assert result is not None, "emails table should exist after init_db()"


def test_save_email_inserts_row(db_instance):
    db_instance.save_email(TEST_EMAIL)
    emails = db_instance.get_emails()
    assert len(emails) == 1
    assert emails[0]["id"] == TEST_EMAIL["id"]


def test_save_email_ignores_duplicate(db_instance):
    db_instance.save_email(TEST_EMAIL)
    db_instance.save_email(TEST_EMAIL)  # duplicate
    emails = db_instance.get_emails()
    assert len(emails) == 1


def test_save_email_missing_field_raises_error(db_instance):
    bad_email = TEST_EMAIL.copy()
    del bad_email["id"]
    with pytest.raises(ValueError, match="Missing required field: id"):
        db_instance.save_email(bad_email)


def test_get_emails_returns_dicts(db_instance):
    db_instance.save_email(TEST_EMAIL)
    emails = db_instance.get_emails()
    assert isinstance(emails, list)
    assert isinstance(emails[0], dict)
    assert emails[0]["id"] == TEST_EMAIL["id"]


def test_get_emails_empty_db_returns_empty_list(db_instance):
    emails = db_instance.get_emails()
    assert emails == []
