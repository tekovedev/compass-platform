from __future__ import annotations

from datetime import UTC, datetime

import boto3
from botocore.exceptions import ClientError

from compass.config import settings
from compass.exceptions import QuotaExceeded


class TokenQuotaStore:
    def __init__(self) -> None:
        self._table = None
        if settings.chat_monthly_usage_table_name:
            dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
            self._table = dynamodb.Table(settings.chat_monthly_usage_table_name)

    @property
    def enabled(self) -> bool:
        return self._table is not None and settings.monthly_token_limit > 0

    @staticmethod
    def _current_month() -> str:
        return datetime.now(UTC).strftime("%Y-%m")

    def ensure_quota(self, user_id: str, estimated_tokens: int) -> None:
        if not self.enabled:
            return

        month = self._current_month()
        response = self._table.get_item(Key={"user_id": user_id, "month": month})  # type: ignore[union-attr]
        item = response.get("Item", {})
        used = int(item.get("tokens_used", 0))
        if used + max(estimated_tokens, 0) > settings.monthly_token_limit:
            raise QuotaExceeded(user_id=user_id, limit=settings.monthly_token_limit, used=used)

    def consume(self, user_id: str, tokens: int) -> None:
        if not self.enabled:
            return

        increment = max(tokens, 0)
        if increment == 0:
            return

        month = self._current_month()
        now = datetime.now(UTC).isoformat()
        remaining = settings.monthly_token_limit - increment

        try:
            self._table.update_item(  # type: ignore[union-attr]
                Key={"user_id": user_id, "month": month},
                UpdateExpression=(
                    "SET tokens_used = if_not_exists(tokens_used, :zero) + :increment, "
                    "token_limit = :limit, "
                    "updated_at = :updated_at, "
                    "created_at = if_not_exists(created_at, :created_at)"
                ),
                ConditionExpression=(
                    "attribute_not_exists(tokens_used) OR tokens_used <= :remaining"
                ),
                ExpressionAttributeValues={
                    ":zero": 0,
                    ":increment": increment,
                    ":limit": settings.monthly_token_limit,
                    ":updated_at": now,
                    ":created_at": now,
                    ":remaining": remaining,
                },
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code == "ConditionalCheckFailedException":
                response = self._table.get_item(Key={"user_id": user_id, "month": month})  # type: ignore[union-attr]
                item = response.get("Item", {})
                used = int(item.get("tokens_used", settings.monthly_token_limit))
                raise QuotaExceeded(user_id=user_id, limit=settings.monthly_token_limit, used=used) from exc
            raise
