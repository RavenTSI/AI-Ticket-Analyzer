from dotenv import load_dotenv
load_dotenv()

import json

from core.loader import load_excel_tickets
from core.embeddings import embed_texts
from core.grouping import group_by_similarity
from core.analysis import analyse_group

DATA_PATH = "data/raw/test_service_tickets.xlsx"
MAX_DISTANCE = 0.35
MAX_DESCRIPTIONS_PER_GROUP = 10


def main():
    print("\n=== LOADING TICKETS ===\n")
    tickets = load_excel_tickets(DATA_PATH)
    print(f"Loaded {len(tickets)} tickets\n")

    print("=== GENERATING EMBEDDINGS ===\n")
    embedding_texts = [t["embedding_text"] for t in tickets]
    embeddings = embed_texts(embedding_texts)
    print("Embeddings generated\n")

    print("=== GROUPING TICKETS (Description-only similarity) ===\n")
    groups, _ = group_by_similarity(embeddings, MAX_DISTANCE)

    meaningful_groups = [g for g in groups if len(g) > 1]
    print(f"Found {len(meaningful_groups)} meaningful groups\n")

    enriched_groups = []

    for idx, group in enumerate(meaningful_groups, start=1):
        print(f"Analysing group {idx}/{len(meaningful_groups)}")

        descriptions = [
            tickets[i]["display_text"]
            for i in group[:MAX_DESCRIPTIONS_PER_GROUP]
        ]

        analysis = analyse_group(descriptions)

        enriched_groups.append({
            "group_id": idx,
            "ticket_indices": group,
            "analysis": analysis,
            "tickets": [tickets[i] for i in group]
        })

    print("\n=== LLM ANALYSIS COMPLETE ===\n")

    # Temporary: print summary to console
    for g in enriched_groups:
        print(f"\n===== GROUP {g['group_id']} =====")
        print(json.dumps(g["analysis"], indent=2))


if __name__ == "__main__":
    main()
