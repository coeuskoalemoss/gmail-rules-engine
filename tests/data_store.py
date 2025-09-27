TEST_EMAIL = {
    "id": "12345",
    "from_email": "sender@example.com",
    "to_email": "me@example.com",
    "subject": "Test email",
    "date": "2025-09-25",
    "snippet": "This is a test snippet",
}

EMAILS = [
    {"id": "1", "subject": "Hello", "from_email": "alice@example.com"},
    {"id": "2", "subject": "World", "from_email": "bob@example.com"},
]


RULES_JSON = [
    {
        "name": "Rule 1",
        "conditions_predicate": "All",
        "conditions": [],
        "actions": ["mark_as_read"],
    },
    {
        "name": "Rule 2",
        "conditions_predicate": "Any",
        "conditions": [],
        "actions": ["mark_as_unread"],
    },
]

EMAIL_MESSAGE = [
    {
        "id": "1",
        "payload": {
            "headers": [
                {"name": "From", "value": "alice@example.com"},
                {"name": "To", "value": "me@example.com"},
                {"name": "Subject", "value": "Hello"},
                {
                    "name": "Date",
                    "value": "Fri, 26 Sep 2025 12:00:00 -0700",
                },
            ]
        },
        "snippet": "Hello snippet",
    },
    {
        "id": "2",
        "payload": {
            "headers": [
                {"name": "From", "value": "bob@example.com"},
                {"name": "To", "value": "me@example.com"},
                {"name": "Subject", "value": "World"},
                {
                    "name": "Date",
                    "value": "Fri, 26 Sep 2025 12:00:00 -0700",
                },
            ]
        },
        "snippet": "World snippet",
    },
]
