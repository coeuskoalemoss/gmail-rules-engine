import pytest
from gmail_utils import GmailAuthenticator
from unittest.mock import Mock

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "token.json"
CLIENT_SECRETS_FILE = "client_secrets.json"
SERVICE_NAME = "gmail"
API_VERSION = "v1"


def test_load_credentials_success(monkeypatch, tmp_path):
    creds_path = tmp_path / "token.json"
    creds_path.write_text("{}")
    logger = Mock()
    auth = GmailAuthenticator.get_gmail_authenticator(
        SCOPES, str(creds_path), CLIENT_SECRETS_FILE, SERVICE_NAME, API_VERSION, logger # noqa
    )
    monkeypatch.setattr("os.path.exists", lambda x: True)
    monkeypatch.setattr(
        "google.oauth2.credentials.Credentials.from_authorized_user_file",
        lambda *a, **k: Mock(),
    )
    auth._load_credentials()
    logger.info.assert_called_with("Credentials loaded successfully.")


def test_load_credentials_error(monkeypatch, tmp_path):
    creds_path = tmp_path / "token.json"
    logger = Mock()
    auth = GmailAuthenticator.get_gmail_authenticator(
        SCOPES, str(creds_path), CLIENT_SECRETS_FILE, SERVICE_NAME, API_VERSION, logger # noqa
    )
    monkeypatch.setattr("os.path.exists", lambda x: True)
    monkeypatch.setattr(
        "google.oauth2.credentials.Credentials.from_authorized_user_file",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    auth._load_credentials()
    logger.error.assert_called()


def test_build_service_success(monkeypatch, tmp_path):
    creds_path = tmp_path / "token.json"
    logger = Mock()
    auth = GmailAuthenticator.get_gmail_authenticator(
        SCOPES, str(creds_path), CLIENT_SECRETS_FILE, SERVICE_NAME, API_VERSION, logger # noqa
    )
    monkeypatch.setattr(
        "gmail_utils.gmail_authenticator.build", lambda *a, **k: "service"
    )
    auth.credentials = Mock()
    auth._build_service()
    assert auth.service == "service"
    logger.info.assert_called_with("Gmail service built successfully.")


def test_build_service_error(monkeypatch, tmp_path):
    creds_path = tmp_path / "token.json"
    logger = Mock()
    auth = GmailAuthenticator.get_gmail_authenticator(
        SCOPES, str(creds_path), CLIENT_SECRETS_FILE, SERVICE_NAME, API_VERSION, logger # noqa
    )

    def fail_build(*a, **k):
        raise Exception("fail")

    monkeypatch.setattr("gmail_utils.gmail_authenticator.build", fail_build)
    auth.credentials = Mock()
    with pytest.raises(Exception):
        auth._build_service()
    logger.error.assert_called()
