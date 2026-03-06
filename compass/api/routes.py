from fastapi import APIRouter
from pydantic import BaseModel

from compass.config import settings
from compass.pipeline.loader import load_documents
from compass.pipeline.chunker import chunk_text
from compass.pipeline.embedder import get_embeddings
from compass.pipeline.store import VectorStore
from compass.pipeline.retriever import retrieve
from compass.generation.generator import generate

router = APIRouter()

_store: VectorStore | None = None


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "healthy"}


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore(
            endpoint=settings.opensearch_endpoint,
            index_name=settings.opensearch_index,
        )
    return _store


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


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest) -> IngestResponse:
    documents = load_documents(request.path)
    all_chunks: list[str] = []
    for doc in documents:
        chunks = chunk_text(doc.content, settings.chunk_size, settings.chunk_overlap)
        all_chunks.extend(chunks)

    embeddings = get_embeddings(all_chunks)
    get_store().add(all_chunks, embeddings)
    return IngestResponse(chunks_stored=len(all_chunks))


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    context_chunks = retrieve(request.query, top_k=request.top_k)
    answer = generate(request.query, context_chunks)
    return QueryResponse(answer=answer, sources=context_chunks)
