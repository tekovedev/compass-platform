from pydantic import BaseModel


class IngestRequest(BaseModel):
    path: str


class IngestResponse(BaseModel):
    chunks_stored: int


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    session_id: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str
    input_tokens: int = 0
    output_tokens: int = 0
