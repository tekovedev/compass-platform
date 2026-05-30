from collections.abc import Mapping

from fastapi import APIRouter, Depends, HTTPException

from compass.api.auth import get_user_id_from_claims, require_auth
from compass.exceptions import GuardrailViolation, QuotaExceeded
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
    claims: Mapping[str, object] = Depends(require_auth),
) -> QueryResponse:
    user_id = get_user_id_from_claims(claims)

    try:
        result = await _query_service.execute(
            request.query,
            user_id=user_id,
            session_id=request.session_id,
            top_k=request.top_k,
        )
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
    except QuotaExceeded as exc:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "token_quota_exceeded",
                "message": "Monthly token quota exceeded",
                "limit": exc.limit,
                "used": exc.used,
            },
        )
    return QueryResponse(
        answer=result.answer,
        sources=result.sources,
        session_id=result.session_id,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )
