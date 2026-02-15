import numpy as np
from sklearn.metrics.pairwise import cosine_distances


ASSET_BOOST = 0.08  # how much to reduce distance if assets overlap


def share_asset(ticket_a_assets, ticket_b_assets):
    if not ticket_a_assets or not ticket_b_assets:
        return False
    return bool(set(ticket_a_assets) & set(ticket_b_assets))


def group_by_similarity(
    embeddings: list[list[float]],
    tickets: list[dict],
    max_distance: float
):
    """
    Deterministic grouping using connected components
    + asset-aware distance adjustment (Hybrid Boost)
    """

    distance_matrix = cosine_distances(embeddings)
    n = len(embeddings)

    visited = set()
    groups = []

    for i in range(n):
        if i in visited:
            continue

        stack = [i]
        group = set()

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            group.add(current)

            neighbors = []

            for j in range(n):
                if j in visited:
                    continue

                distance = distance_matrix[current][j]

                # Asset-aware adjustment
                if share_asset(
                    tickets[current]["assets"],
                    tickets[j]["assets"]
                ):
                    distance -= ASSET_BOOST

                if distance <= max_distance:
                    neighbors.append(j)

            stack.extend(neighbors)

        groups.append(sorted(group))

    return groups, distance_matrix
