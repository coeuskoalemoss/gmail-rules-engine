import json
from utils import rules_engine


class RuleProcessor:
    """
    Applies automation rules to emails stored in the database.
    Loads rules from a JSON file, evaluates them using the rules engine,
    and applies corresponding actions via the Gmail API.
    """

    def __init__(self, email_db, service, rules_file_path, logger=None):
        """
        Initialize the EmailRuleProcessor.

        Args:
            email_db: Instance of EmailDatabase class.
            service: Authenticated Gmail API service object.
            rules_file_path (str): Path to the email rules JSON file.
        """
        self.email_db = email_db
        self.service = service
        self.rules_file_path = rules_file_path
        self.rules = []
        self.logger = logger

    def load_rules(self):
        """Load automation rules from the JSON file."""
        try:
            with open(self.rules_file_path, "r") as f:
                self.rules = json.load(f)
            self.logger.info(f"Loaded {len(self.rules)} rule(s) from {self.rules_file_path}") # noqa
        except FileNotFoundError:
            self.logger.info(f"Email Rules Automation File not found: {self.rules_file_path}") # noqa
        except json.JSONDecodeError as e:
            self.logger.info(f"Invalid JSON format in rules file: {e}")

    def process_emails(self):
        """
        Process all emails from the database against loaded rules.
        """
        if not self.rules:
            self.logger.info("No rules loaded. Call `load_rules()` first.")
            return

        emails = self.email_db.get_emails()
        if not emails:
            self.logger.info("No emails in the database to process.")
            return

        self.logger.info(f"Processing {len(emails)} emails with {len(self.rules)} rules...") # noqa

        for email in emails:
            for rule in self.rules:
                try:
                    if rules_engine.evaluate_rule(
                            email,
                            rule,
                            ):
                        actions = rule.get("actions", [])
                        rules_engine.apply_actions(
                            email,
                            actions,
                            self.service,
                        )
                        self.logger.info(
                            f"Applied rule '{rule.get('name')}' to email: '{email.get('subject')}'" # noqa
                        )
                except Exception as e:
                    self.logger.info(f"Error applying rule '{rule.get('name', 'Unnamed')}': {e}") # noqa

        self.logger.info("Finished processing all emails.")
