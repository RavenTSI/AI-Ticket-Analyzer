import pandas as pd
import re


def find_description_fields(row: dict):
    """
    Tries to locate description-like fields defensively.
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


def extract_assets(text: str):
    """
    Extract IPs, hostnames, URLs and server-like tokens.
    """

    assets = set()

    if not text:
        return []

    # IP address pattern
    ip_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"

    # URL pattern
    url_pattern = r"https?://[^\s]+"

    # Hostname / server-like pattern (server01, auth-prod-01, etc.)
    hostname_pattern = r"\b[a-zA-Z0-9\-]{3,}\.(?:com|net|org|local|corp|internal)\b"
    server_pattern = r"\b(?:srv|server|auth|ping|iam|dc|mfa)[a-zA-Z0-9\-]*\b"

    matches = (
        re.findall(ip_pattern, text)
        + re.findall(url_pattern, text)
        + re.findall(hostname_pattern, text)
        + re.findall(server_pattern, text)
    )

    for m in matches:
        assets.add(m.lower())

    return list(assets)


def load_excel_tickets(path: str):
    df = pd.read_excel(path)

    tickets = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        canonical_description = find_description_fields(row_dict)

        if canonical_description is None:
            canonical_description = "no description provided"

        assets = extract_assets(canonical_description)

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
            "embedding_text": canonical_description,
            "assets": assets
        }

        tickets.append(ticket)

    return tickets
