from fastapi import APIRouter, Depends, HTTPException

from compass.api.auth import require_auth
from compass.exceptions import GuardrailViolation
from compass.api.schemas import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
)
from compass.services.query import QueryService
from compass.services.ingest import IngestService

router = APIRouter()

_query_service = QueryService()
_ingest_service = IngestService()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "healthy"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    request: IngestRequest,
    _: dict = Depends(require_auth),
) -> IngestResponse:
    chunks_stored = await _ingest_service.execute(request.path)
    return IngestResponse(chunks_stored=chunks_stored)


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    _: dict = Depends(require_auth),
) -> QueryResponse:
    try:
        result = await _query_service.execute(request.query, top_k=request.top_k)
    except GuardrailViolation as exc:
        if exc.source == "INPUT":
            raise HTTPException(
                status_code=400,
                detail={"error": "guardrail_input_violation", "message": exc.result.message},
            )
        raise HTTPException(
            status_code=500,
            detail={"error": "guardrail_output_violation", "message": exc.result.message},
        )
    return QueryResponse(answer=result.answer, sources=result.sources)
