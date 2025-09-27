# Gmail Rules Processor

This project automates the processing of Gmail emails based on a set of user-defined rules. It fetches emails from a specified Gmail account, stores them in a local database, and applies actions such as moving or marking emails as read/unread based on rules defined in a JSON file.

## Features

- Fetches emails from your Gmail account.
- Stores email data locally in an SQLite database.
- Processes emails based on configurable rules (e.g., moving emails to specific folders, marking as read).
- Securely authenticates with the Gmail API using OAuth 2.0.
- Logs activities for easy monitoring and debugging.

## Prerequisites

- Python 3.8+
- `pip` for installing packages

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/coeuskoalemoss/gmail-rules-engine.git
    cd gmail_rules_project
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    #for WSL or Ubuntu
    python3 -m venv myvenv
    source myvenv/bin/activate
    ```

    ```bash
    #for Windows
    python -m venv myvenv
    myvenv/Scripts/activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Gmail API Credentials:**

    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Enable the "Gmail API".
    - Create credentials for an "OAuth client ID".
    - Select "Desktop app" as the application type.
    - Download the credentials JSON file and save it as `config/credentials.json` in the project directory.
    - Refer to the `config/credentials.example.json` for file structure

5.  **Run the initial authentication:**
    - The first time you run the application, it will open a browser window for you to authorize access to your Gmail account.
    - After authorization, a `token.json` file will be created in the root directory. This file stores your access and refresh tokens.

## Usage

To run the email processing script, execute the `main.py` file:

```bash
python main.py
```

The script will fetch new emails, process them according to your rules, and log its actions to `logs/my_app.log`.

## Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

## Run Test Coverage

```bash
pytest --cov=gmail_utils --cov=database --cov=utils --cov=logger --cov=config --cov=main --cov=rule_processor tests/
```

## Project Structure

```
gmail_rules_project/
├── config/
│   ├── credentials.example.json  # Gmail API credentials example
│   ├── credentials.json  # Gmail API credentials
│   └── rules.json        # Email processing rules
├── database/
│   └── email_database.py # Manages the SQLite database
├── gmail_utils/
│   ├── gmail_authenticator.py # Handles OAuth 2.0 authentication
│   └── gmail_email_fetcher.py # Fetches emails from Gmail
├── logs/
│   └── my_app.log        # Application logs
├── tests/                # Unit tests
├── main.py               # Main script to run the application
├── rule_processor.py     # Processes emails based on the defined rules
├── requirements.txt      # Python dependencies
└── README.md             # This file
```
