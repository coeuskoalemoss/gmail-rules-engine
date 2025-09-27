from gmail_utils import GmailAuthenticator, GmailEmailFetcher
from rule_processor import RuleProcessor
from database import EmailDatabase
from config import (
    SCOPES,
    GOOGLE_AUTH_TOKEN_FILE,
    SERVICE_NAME,
    GOOGLE_API_VERSION,
    GOOGLE_CLIENT_SECRETS_FILE,
    EMAIL_AUTOMATION_RULES_FILE,
    DB_NAME,
)
from logger import LoggerInstance


class GmailRulesPipeline:
    def __init__(self):
        self.logger = LoggerInstance(
            name=__name__, log_folder="logs", log_file="my_app.log"
        ).get_logger()
        # Initialize Gmail Authenticator
        self.gmail_authenticator = GmailAuthenticator(
            SCOPES,
            GOOGLE_AUTH_TOKEN_FILE,
            GOOGLE_CLIENT_SECRETS_FILE,
            SERVICE_NAME,
            GOOGLE_API_VERSION,
            logger=self.logger,
        )
        self.email_db = EmailDatabase(DB_NAME, self.logger)
        self.service = None
        self.email_fetcher = None
        self.rules_processor = None

    def authenticate_gmail(self):
        """Authenticate and return Gmail service object."""
        self.logger.info("Authenticating with Gmail...")
        self.service = self.gmail_authenticator.authenticate()
        self.logger.info("Gmail authentication successful.")

    def fetch_emails(self, max_results=6):
        """Fetch latest emails from Gmail and save to DB."""
        self.logger.info(f"Fetching up to {max_results} emails...")
        self.email_fetcher = GmailEmailFetcher(self.service, self.email_db, self.logger) # noqa
        self.email_fetcher.fetch_and_save_emails(max_results=max_results)
        self.logger.info("Email fetching completed.")

    def process_emails(self):
        """Process emails using automation rules."""
        self.logger.info("Processing emails using rules...")
        self.rules_processor = RuleProcessor(
            self.email_db, self.service, EMAIL_AUTOMATION_RULES_FILE, self.logger # noqa
        )
        self.rules_processor.load_rules()
        self.rules_processor.process_emails()
        self.logger.info("Email processing completed.")

    def run_pipeline(self):
        """Run the complete Gmail rules pipeline."""
        self.logger.info("Starting Gmail Rules Pipeline...")
        self.authenticate_gmail()
        self.fetch_emails()
        self.process_emails()
        self.logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    pipeline = GmailRulesPipeline()
    pipeline.run_pipeline()
