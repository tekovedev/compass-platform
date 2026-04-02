from pydantic import BaseModel


class IngestRequest(BaseModel):
    path: str


class IngestResponse(BaseModel):
    chunks_stored: int


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
