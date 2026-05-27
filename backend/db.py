from supabase import create_client, Client

from .config import SUPABASE_URL, SUPABASE_SERVICE_KEY, TOP_K

_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def _to_pgvector(vec: list[float]) -> str:
    # pgvector expects '[0.1,0.2,...]' text form. Passing a raw JSON array
    # through PostgREST does not reliably cast to vector and can silently
    # produce zero matches.
    return "[" + ",".join(repr(float(x)) for x in vec) + "]"


def insert_chunks(rows: list[dict]) -> None:
    if not rows:
        return
    formatted = [{**row, "embedding": _to_pgvector(row["embedding"])} for row in rows]
    _client.table("documents").insert(formatted).execute()


def match_documents(query_embedding: list[float], match_count: int = TOP_K) -> list[dict]:
    response = _client.rpc(
        "match_documents",
        {
            "query_embedding": _to_pgvector(query_embedding),
            "match_count": match_count,
        },
    ).execute()
    return response.data or []
