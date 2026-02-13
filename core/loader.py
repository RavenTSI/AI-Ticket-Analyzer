import pandas as pd


def find_description_fields(row: dict):
    """
    Tries to locate description-like fields in a defensive way.
    Works with current sample data and future real datasets.
    """
    possible_keys = [
        "Long Description",
        "Short Description",
        "Issue Description",
        "Description",
        "Issue description",
        "Summary",
    ]

    for key in possible_keys:
        if key in row:
            value = row.get(key)
            if value is not None:
                text = str(value).strip()
                if text and text.lower() != "nan":
                    return text.lower()

    return None


def load_excel_tickets(path: str):
    df = pd.read_excel(path)

    tickets = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        canonical_description = find_description_fields(row_dict)

        if canonical_description is None:
            canonical_description = "no description provided"

        ticket = {
            "ticket_id": row_dict.get("Ticket ID"),
            "display_text": (
                f"Ticket Summary\n"
                f"--------------\n"
                f"Ticket ID: {row_dict.get('Ticket ID')}\n"
                f"Date Created: {row_dict.get('Date Created')}\n"
                f"Department: {row_dict.get('Department')}\n"
                f"Assigned To: {row_dict.get('Assigned To')}\n"
                f"Priority: {row_dict.get('Priority')}\n"
                f"Status: {row_dict.get('Status')}\n\n"
                f"Issue Description:\n"
                f"{canonical_description}"
            ),
            "embedding_text": canonical_description
        }

        tickets.append(ticket)

    return tickets
