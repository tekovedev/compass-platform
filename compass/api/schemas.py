from typing import Literal

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str
    input_tokens: int = 0
    output_tokens: int = 0


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: int
    rating: Literal["up", "down"]
    question: str
    answer: str


class FeedbackResponse(BaseModel):
    status: str = "ok"
