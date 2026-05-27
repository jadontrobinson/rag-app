import voyageai

from .config import VOYAGE_API_KEY, EMBEDDING_MODEL

_client = voyageai.Client(api_key=VOYAGE_API_KEY)


def embed_documents(texts: list[str]) -> list[list[float]]:
    result = _client.embed(texts, model=EMBEDDING_MODEL, input_type="document")
    return result.embeddings


def embed_query(text: str) -> list[float]:
    result = _client.embed([text], model=EMBEDDING_MODEL, input_type="query")
    return result.embeddings[0]
