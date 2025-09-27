import pytest
from database.email_database import EmailDatabase
import os
import sqlite3
from unittest.mock import Mock

TEST_EMAIL = {
    "id": "12345",
    "from_email": "sender@example.com",
    "to_email": "me@example.com",
    "subject": "Test email",
    "date": "2025-09-25",
    "snippet": "This is a test snippet",
}

TEST_DB = "test_emails.db"


@pytest.fixture
def db_instance():
    """Fixture to use a fresh test DB for each test."""
    mock_logger = Mock()
    db = EmailDatabase(db_name=TEST_DB, logger=mock_logger)

    # Clear table before test
    with sqlite3.connect(TEST_DB) as conn:
        conn.execute("DELETE FROM emails")

    yield db

    # Teardown: remove test DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_init_db_creates_table(db_instance):
    # The table is created in the constructor, which is called by the fixture.
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()
    c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
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
    assert len(emails) == 1  # still only one row


def test_save_email_missing_field_raises_error(db_instance):
    bad_email = TEST_EMAIL.copy()
    del bad_email["id"]  # remove primary key
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
