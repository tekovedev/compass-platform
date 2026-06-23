from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Literal

import boto3

from compass.config import settings

logger = logging.getLogger(__name__)

Rating = Literal["up", "down"]


class FeedbackStore:
    def __init__(self) -> None:
        self._table = None

        if settings.feedback_table_name:
            dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
            self._table = dynamodb.Table(settings.feedback_table_name)

    @property
    def enabled(self) -> bool:
        return self._table is not None

    def save(
        self,
        *,
        user_id: str,
        session_id: str,
        message_id: int,
        rating: Rating,
        question: str,
        answer: str,
    ) -> None:
        if not self.enabled:
            logger.warning("[FEEDBACK] table not configured — skipping save")
            return

        item = {
            "session_id": session_id,
            "message_id": message_id,
            "user_id": user_id,
            "rating": rating,
            "question": question,
            "answer": answer,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._table.put_item(Item=item)  # type: ignore[union-attr]
        logger.info("[FEEDBACK] saved | session_id=%s | message_id=%s | rating=%s", session_id, message_id, rating)
