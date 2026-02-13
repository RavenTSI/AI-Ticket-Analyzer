import numpy as np
from sklearn.metrics.pairwise import cosine_distances


def group_by_similarity(
    embeddings: list[list[float]],
    max_distance: float
):
    """
    Deterministic grouping using connected components.
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

            neighbors = [
                j for j in range(n)
                if j not in visited and distance_matrix[current][j] <= max_distance
            ]

            stack.extend(neighbors)

        groups.append(sorted(group))

    return groups, distance_matrix
