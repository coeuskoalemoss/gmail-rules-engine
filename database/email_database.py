import sqlite3


class EmailDatabase:
    """
    Handles all database operations for storing and managing emails.
    """

    def __init__(self, db_name, logger=None):
        """
        Initialize the EmailDatabase with a database name.

        Args:
            db_name (str): The name or path of the SQLite database file.
        """
        self.db_name = db_name
        self.logger = logger
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the SQLite database and create the 'emails' table"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS emails (
                        id TEXT PRIMARY KEY,
                        from_email TEXT,
                        to_email TEXT,
                        subject TEXT,
                        date TEXT,
                        snippet TEXT,
                        is_read INTEGER DEFAULT 0
                    )
                    """
                )
            self.logger.info("Database initialized and table ready.")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")

    def save_email(self, email):
        """
        Save an email to the database.

        Args:
            email : A dictionary containing email fields.
        Raises:
            ValueError: If any required field is missing.
        """
        try:
            required_keys = ["id", "from_email", "to_email", "subject", "date", "snippet"] # noqa
            for key in required_keys:
                if key not in email:
                    raise ValueError(f"Missing required field: {key}")

            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO emails
                    (id, from_email, to_email, subject, date, snippet)
                    VALUES (
                        :id, :from_email, :to_email, :subject, :date, :snippet
                    )
                    """,
                    email,
                )
            self.logger.info(f"Saved email: {email['id']}")
        except ValueError as ve:
            self.logger.error(f"Error saving email {email.get('id', '')}: {ve}") # noqa
            raise
        except Exception as e:
            self.logger.error(f"Error saving email {email.get('id', '')}: {e}")

    def get_emails(self):
        """
        Fetch all emails from the database.

        Returns:
            list[dict]: List of email records as dictionaries.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    (
                        "SELECT id, from_email, to_email, subject, date, "
                        "snippet, is_read FROM emails"
                    )
                )
                rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "from_email": row[1],
                    "to_email": row[2],
                    "subject": row[3],
                    "date": row[4],
                    "snippet": row[5],
                    "is_read": row[6],
                }
                for row in rows
            ]
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return []
