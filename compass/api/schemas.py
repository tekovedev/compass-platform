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
