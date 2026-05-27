from groq import Groq

from .config import GROQ_API_KEY, ANSWER_MODEL, MAX_TOKENS, TOP_K
from .embeddings import embed_query
from .db import match_documents

_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using the provided context.

Rules:
- Use only the information in the provided context to answer.
- If the context does not contain the answer, say you don't know based on the available documents.
- Cite sources inline using the [source: filename] format when you use them.
- Be concise and direct."""


def _format_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(f"[source: {c['source']} | chunk {c['chunk_index']}]\n{c['content']}")
    return "\n\n---\n\n".join(parts)


def answer(question: str, top_k: int = TOP_K) -> dict:
    query_vec = embed_query(question)
    chunks = match_documents(query_vec, match_count=top_k)

    if not chunks:
        return {
            "answer": "I don't have any documents indexed yet, so I can't answer that.",
            "sources": [],
        }

    context = _format_context(chunks)
    user_message = f"Context:\n\n{context}\n\nQuestion: {question}"

    response = _client.chat.completions.create(
        model=ANSWER_MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    answer_text = response.choices[0].message.content or ""

    sources = [
        {
            "source": c["source"],
            "chunk_index": c["chunk_index"],
            "similarity": c["similarity"],
            "content": c["content"],
        }
        for c in chunks
    ]

    return {"answer": answer_text, "sources": sources}
