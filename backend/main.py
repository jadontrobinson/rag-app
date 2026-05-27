from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .rag import answer
from .config import TOP_K

app = FastAPI(title="RAG Q&A API")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=TOP_K, ge=1, le=20)


class Source(BaseModel):
    source: str
    chunk_index: int
    similarity: float
    content: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    try:
        result = answer(req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return QueryResponse(**result)
