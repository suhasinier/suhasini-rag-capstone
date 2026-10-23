"""Week 7 API — CBSE Class 9 RAG using Qdrant."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.rag.qdrant_rag import ask_rag

app = FastAPI(title="CBSE Class 9 RAG API — W7")


class Question(BaseModel):
    question: str = Field(..., min_length=1)


class RAGAnswer(BaseModel):
    answer: str | None
    sources: list[str]
    chunk_ids: list[str]
    tokens_in: int
    tokens_out: int


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/ask_batched", response_model=RAGAnswer)
async def ask_batched(q: Question) -> RAGAnswer:
    try:
        result = ask_rag(q.question)
        return RAGAnswer(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The RAG request failed. Check the application logs.",
        ) from exc


@app.post("/ask")
async def ask(q: Question) -> RAGAnswer:
    return await ask_batched(q)
