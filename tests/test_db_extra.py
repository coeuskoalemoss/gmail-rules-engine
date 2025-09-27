from database.email_database import EmailDatabase
from unittest.mock import Mock
import sqlite3


def test_init_db_logs(monkeypatch, tmp_path):
    db_path = tmp_path / "emails.db"
    logger = Mock()
    EmailDatabase(str(db_path), logger=logger)
    logger.info.assert_called_with("Database initialized and table ready.")


def test_init_db_error(monkeypatch, tmp_path):
    logger = Mock()
    # Simulate sqlite3.connect raising an error
    monkeypatch.setattr(
        sqlite3, "connect", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")) # noqa
    )
    EmailDatabase("bad.db", logger=logger)
    logger.error.assert_called()


def test_save_email_error(monkeypatch, tmp_path):
    db_path = tmp_path / "emails.db"
    logger = Mock()
    db = EmailDatabase(str(db_path), logger=logger)
    # Simulate sqlite3.connect raising an error
    monkeypatch.setattr(
        sqlite3, "connect", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")) # noqa
    )
    email = {
        "id": "1",
        "from_email": "a",
        "to_email": "b",
        "subject": "s",
        "date": "d",
        "snippet": "snip",
    }
    db.save_email(email)
    logger.error.assert_called()


def test_get_emails_error(monkeypatch, tmp_path):
    db_path = tmp_path / "emails.db"
    logger = Mock()
    db = EmailDatabase(str(db_path), logger=logger)
    monkeypatch.setattr(
        sqlite3, "connect", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")) # noqa
    )
    result = db.get_emails()
    assert result == []
    logger.error.assert_called()
