from googleapiclient.errors import HttpError


class GmailEmailFetcher:
    """
    Handles fetching emails from Gmail and saving them to the database.
    """

    def __init__(self, service, email_db, logger=None, user_id="me"):
        """
        Initialize the GmailEmailFetcher.

        Args:
            service: Authenticated Gmail API service object.
            email_db: Instance of EmailDatabase class.
            user_id (str): Gmail user ID.
        """
        self.service = service
        self.email_db = email_db
        self.user_id = user_id
        self.logger = logger

    def fetch_and_save_emails(self, max_results=5):
        """
        Fetch emails from Gmail and save them to the database.

        Args:
            max_results (int): Maximum number of emails to fetch.
        """
        try:
            # List messages
            results = (
                self.service.users()
                .messages()
                .list(userId=self.user_id, maxResults=max_results)
                .execute()
            )
            messages = results.get("messages", [])

            if not messages:
                self.logger.error("No messages found.")
                return

            self.logger.info(
                f"""Found {len(messages)} messages."""
                f"""Fetching details"""
            )

            for msg in messages:
                msg_id = msg["id"]
                msg_detail = (
                    self.service.users()
                    .messages()
                    .get(userId=self.user_id, id=msg_id, format="full")
                    .execute()
                )

                headers = {
                    h["name"]: h["value"]
                    for h in msg_detail["payload"].get("headers", [])
                }

                email_data = {
                    "id": msg_id,
                    "from_email": headers.get("From", ""),
                    "to_email": headers.get("To", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": msg_detail.get("snippet", ""),
                }

                self.email_db.save_email(email=email_data)

            self.logger.info(f"Successfully fetched and saved {len(messages)} emails.") # noqa

        except HttpError as error:
            self.logger.info(f"An error occurred while fetching emails: {error}") # noqa
