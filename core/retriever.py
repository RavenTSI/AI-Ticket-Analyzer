import faiss
import numpy as np
from typing import List, Dict, Tuple


class TicketRetriever:
    def __init__(self, embeddings: List[List[float]], tickets: List[Dict]):
        self.embeddings = np.array(embeddings).astype("float32")
        self.tickets = tickets

        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.embeddings)

    def find_similar(
        self,
        query_index: int,
        max_results: int = 10,
        distance_threshold: float = 1.1,
    ) -> List[Tuple[int, float]]:
        """
        Return indices AND distances of tickets that are meaningfully similar.
        """
        query_vector = self.embeddings[query_index].reshape(1, -1)
        distances, indices = self.index.search(query_vector, max_results)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == query_index:
                continue
            if dist <= distance_threshold:
                results.append((idx, dist))

        return results
