import os
from typing import List
from openai import OpenAI


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.
    OpenAI client is created only when this function is called.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set. Embeddings cannot be generated.")

    client = OpenAI(api_key=api_key)

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    return [item.embedding for item in response.data]
