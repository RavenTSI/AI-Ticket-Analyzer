import pandas as pd
from pathlib import Path


def load_excel_tickets(file_path: str) -> list[str]:
    """
    Load an Excel file and convert each row into a structured,
    honest, human-readable ticket summary.
    """

    path = Path(file_path)
    df = pd.read_excel(path)

    tickets_as_text = []

    for _, row in df.iterrows():
        ticket_text = f"""
Ticket Summary
--------------
Ticket ID: {row.get('Ticket ID', 'Unknown')}
Date Created: {row.get('Date Created', 'Unknown')}
Department: {row.get('Department', 'Unknown')}
Assigned To: {row.get('Assigned To', 'Unassigned')}
Priority: {row.get('Priority', 'Unknown')}
Status: {row.get('Status', 'Unknown')}

Issue Description:
{row.get('Description', '').strip()}
""".strip()

        tickets_as_text.append(ticket_text)

    return tickets_as_text
