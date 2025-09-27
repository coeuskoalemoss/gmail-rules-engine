from datetime import datetime


def evaluate_string(field_value, predicate, value):
    field_value = field_value or ""  # Handle None
    value = value or ""
    predicate = predicate.lower()

    if predicate == "contains":
        return value.lower() in field_value.lower()
    elif predicate == "does not contain":
        return value.lower() not in field_value.lower()
    elif predicate == "equals":
        return field_value.lower() == value.lower()
    elif predicate == "does not equal":
        return field_value.lower() != value.lower()
    else:
        raise ValueError(f"Unknown string predicate: {predicate}")


def evaluate_date(field_value, predicate, value):
    """
    field_value: date string from Gmail header
    value: number of days for comparison
    """
    try:
        email_date = datetime.strptime(
            field_value[:25], "%a, %d %b %Y %H:%M:%S"
        )  # Gmail date format
    except Exception:
        return False

    now = datetime.now()
    days = int(value)
    predicate = predicate.lower()

    if predicate in ["less than", "is_less_than"]:
        return (now - email_date).days < days
    elif predicate in ["greater than", "is_greater_than"]:
        return (now - email_date).days > days
    else:
        raise ValueError(f"Unknown date predicate: {predicate}")


def evaluate_condition(email, condition):
    field = condition.get("field").lower()
    predicate = condition.get("predicate")
    value = condition.get("value")

    if field in ["from", "from_email"]:
        return evaluate_string(email.get("from_email"), predicate, value)
    elif field in ["to", "to_email"]:
        return evaluate_string(email.get("to_email"), predicate, value)
    elif field in ["subject"]:
        return evaluate_string(email.get("subject"), predicate, value)
    elif field in ["snippet", "message"]:
        return evaluate_string(email.get("snippet"), predicate, value)
    elif field in ["date", "date received", "received"]:
        return evaluate_date(email.get("date"), predicate, value)
    else:
        raise ValueError(f"Unknown field: {field}")


def evaluate_rule(email, rule):
    conditions = rule.get("conditions", [])
    overall = rule.get("conditions_predicate", "All").lower()  # "all" or "any"

    results = [evaluate_condition(email, cond) for cond in conditions]

    if overall == "all":
        return all(results)
    elif overall == "any":
        return any(results)
    else:
        raise ValueError(f"Unknown overall predicate: {overall}")


def get_label_id(service, label_name):
    """
    Returns the Gmail label ID for a given label name.
    Creates the label if it doesn't exist.
    Logs existing labels and any created label.
    """
    labels_response = service.users().labels().list(userId="me").execute()
    labels_dict = {
        label["name"]: label["id"] for label in labels_response.get("labels")
    }

    label_id = labels_dict.get(label_name)
    if label_id:
        return label_id

    new_label = (
        service.users()
        .labels()
        .create(
            userId="me",
            body={
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        .execute()
    )
    return new_label["id"]


def apply_actions(email, actions, service=None):
    """
    email: email dict
    actions: list of actions from rule
    service: Gmail service object (required for API actions)
    """
    for action in actions:
        action_lower = action.lower()
        if action_lower == "mark_as_read" and service:
            service.users().messages().modify(
                userId="me", id=email["id"], body={"removeLabelIds": ["UNREAD"]}  # noqa
            ).execute()

        elif action_lower == "mark_as_unread" and service:
            service.users().messages().modify(
                userId="me", id=email["id"], body={"addLabelIds": ["UNREAD"]}
            ).execute()

        elif action_lower.startswith("move_to") and service:
            # e.g., "move_to:LabelName"
            label_name = action.split(":", 1)[1].strip()
            label_id = get_label_id(service, label_name)  # check/create label
            service.users().messages().modify(
                userId="me", id=email["id"], body={"addLabelIds": [label_id]}
            ).execute()
