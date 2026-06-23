import asyncio
import logging
from collections.abc import Mapping

from fastapi import APIRouter, Depends, HTTPException

from compass.api.auth import get_user_id_from_claims, require_auth
from compass.exceptions import GuardrailViolation, QuotaExceeded
from compass.api.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    QueryRequest,
    QueryResponse,
)
from compass.infrastructure.feedback_store import FeedbackStore
from compass.services.query import QueryService

logger = logging.getLogger(__name__)

router = APIRouter()

_query_service = QueryService()
_feedback_store = FeedbackStore()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "healthy"}


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    claims: Mapping[str, object] = Depends(require_auth),
) -> QueryResponse:
    user_id = get_user_id_from_claims(claims)
    logger.info("[API] POST /query | user_id=%s | session_id=%s | query=%r", user_id, request.session_id, request.query)

    try:
        result = await _query_service.execute(
            request.query,
            user_id=user_id,
            session_id=request.session_id,
        )
    except GuardrailViolation as exc:
        if exc.source == "INPUT":
            logger.warning("[API] guardrail input violation | user_id=%s | message=%s", user_id, exc.result.message)
            raise HTTPException(
                status_code=400,
                detail={"error": "guardrail_input_violation", "message": exc.result.message},
            )
        logger.warning("[API] guardrail output violation | user_id=%s | message=%s", user_id, exc.result.message)
        raise HTTPException(
            status_code=500,
            detail={"error": "guardrail_output_violation", "message": exc.result.message},
        )
    except QuotaExceeded as exc:
        logger.warning("[API] quota exceeded | user_id=%s | used=%s | limit=%s", user_id, exc.used, exc.limit)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "token_quota_exceeded",
                "message": "Monthly token quota exceeded",
                "limit": exc.limit,
                "used": exc.used,
            },
        )
    logger.info("[API] response | session_id=%s | sources=%s | answer=%r", result.session_id, result.sources, result.answer)
    return QueryResponse(
        answer=result.answer,
        sources=result.sources,
        session_id=result.session_id,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(
    request: FeedbackRequest,
    claims: Mapping[str, object] = Depends(require_auth),
) -> FeedbackResponse:
    user_id = get_user_id_from_claims(claims)
    logger.info("[API] POST /feedback | user_id=%s | session_id=%s | message_id=%s | rating=%s", user_id, request.session_id, request.message_id, request.rating)
    await asyncio.to_thread(
        _feedback_store.save,
        user_id=user_id,
        session_id=request.session_id,
        message_id=request.message_id,
        rating=request.rating,
        question=request.question,
        answer=request.answer,
    )
    return FeedbackResponse()
