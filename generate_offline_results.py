import os
import json
from dotenv import load_dotenv

load_dotenv()

from core.loader import load_excel_tickets
from core.embeddings import embed_texts
from core.grouping import group_by_similarity
from core.analysis import analyse_group

DATA_PATH = "data/raw/test_service_tickets.xlsx"
MAX_DISTANCE = 0.35
MAX_DESCRIPTIONS_PER_GROUP = 8
OUTPUT_PATH = "data/offline/offline_results.json"


def main():
    print("Loading tickets...")
    tickets = load_excel_tickets(DATA_PATH)
    print(f"{len(tickets)} tickets loaded")

    print("Generating embeddings...")
    embedding_texts = [t["embedding_text"] for t in tickets]
    embeddings = embed_texts(embedding_texts)
    print("Embeddings generated")

    print("Grouping tickets...")
    groups, _ = group_by_similarity(embeddings, MAX_DISTANCE)

    meaningful_groups = [g for g in groups if len(g) > 1]
    print(f"{len(meaningful_groups)} meaningful groups found")

    results = []

    for idx, group in enumerate(meaningful_groups, start=1):
        print(f"Analysing Group {idx}")

        descriptions = [
            tickets[i]["embedding_text"]
            for i in group[:MAX_DESCRIPTIONS_PER_GROUP]
        ]

        analysis = analyse_group(descriptions)

        group_data = {
            "group_number": idx,
            "tickets": [
                {
                    "display_text": tickets[i]["display_text"],
                    "embedding_text": tickets[i]["embedding_text"]
                }
                for i in group
            ],
            "analysis": analysis
        }

        results.append(group_data)

    print("Saving offline results...")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("Offline results saved successfully!")


if __name__ == "__main__":
    main()
