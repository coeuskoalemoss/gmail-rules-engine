import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


class GmailAuthenticator:
    """
    Handles Gmail API authentication using OAuth2.
    Automatically loads, refreshes, and saves credentials.
    """

    def __init__(
        self, scopes, token_file, client_secrets_file, service_name,
        api_version, logger=None
    ):
        """
        Initialize the GmailAuthenticator with configuration parameters.

        Args:
            scopes (list): List of OAuth scopes.
            token_file (str): Path to the stored token JSON file.
            client_secrets_file (str): Path to the client secrets JSON file.
            service_name (str): Name of the Google API service (e.g., 'gmail').
            api_version (str): Version of the API (e.g., 'v1').
        """
        self.scopes = scopes
        self.token_file = token_file
        self.client_secrets_file = client_secrets_file
        self.service_name = service_name
        self.api_version = api_version
        self.credentials = None
        self.service = None
        self.logger = logger

    def authenticate(self):
        """
        Authenticate with Gmail API and return a service object.
        """
        self._load_credentials()
        self._ensure_valid_credentials()
        self._build_service()
        return self.service

    def _load_credentials(self):
        """Load credentials from the token file if available."""
        try:
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_file, self.scopes
                )
            self.logger.info("Credentials loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")

    def _ensure_valid_credentials(self):
        """Ensure credentials are valid;
        refresh or re-authenticate if needed."""
        try:
            if not self.credentials or not self.credentials.valid:
                if (
                    self.credentials
                    and self.credentials.expired
                    and self.credentials.refresh_token
                ):
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, self.scopes
                    )
                    self.credentials = flow.run_local_server(port=0)
                # Save new credentials
                self.logger.info("Saving new credentials to token file.")
                with open(self.token_file, "w") as token_file:
                    token_file.write(self.credentials.to_json())
            self.logger.info("Credentials are valid.")
        except Exception as e:
            self.logger.error(f"Error during authentication: {e}")
            raise e

    def _build_service(self):
        """Build the Gmail API service object."""
        try:
            self.service = build(
                self.service_name,
                self.api_version,
                credentials=self.credentials
            )
            self.logger.info("Gmail service built successfully.")
        except Exception as e:
            self.logger.error(f"Error building Gmail service: {e}")
            raise e
