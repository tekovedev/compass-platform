from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key

from compass.config import settings

MessageRole = Literal["user", "assistant"]


@dataclass(frozen=True)
class ConversationTurn:
    role: MessageRole
    content: str
    created_at: str
    message_id: str


class ConversationStore:
    def __init__(self) -> None:
        self._sessions_table = None
        self._conversations_table = None

        if settings.chat_sessions_table_name and settings.chat_conversations_table_name:
            dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
            self._sessions_table = dynamodb.Table(settings.chat_sessions_table_name)
            self._conversations_table = dynamodb.Table(settings.chat_conversations_table_name)

    @property
    def enabled(self) -> bool:
        return self._sessions_table is not None and self._conversations_table is not None

    def upsert_session(self, user_id: str, session_id: str | None, title: str | None = None) -> str:
        resolved_session_id = session_id or str(uuid4())
        if not self.enabled:
            return resolved_session_id

        now = datetime.now(UTC).isoformat()
        self._sessions_table.update_item(  # type: ignore[union-attr]
            Key={"user_id": user_id, "session_id": resolved_session_id},
            UpdateExpression=(
                "SET updated_at = :updated_at, "
                "created_at = if_not_exists(created_at, :created_at), "
                "title = if_not_exists(title, :title)"
            ),
            ExpressionAttributeValues={
                ":updated_at": now,
                ":created_at": now,
                ":title": title or "New Conversation",
            },
        )
        return resolved_session_id

    def touch_session(self, user_id: str, session_id: str) -> None:
        if not self.enabled:
            return

        self._sessions_table.update_item(  # type: ignore[union-attr]
            Key={"user_id": user_id, "session_id": session_id},
            UpdateExpression="SET updated_at = :updated_at",
            ExpressionAttributeValues={":updated_at": datetime.now(UTC).isoformat()},
        )

    def append_message(
        self,
        user_id: str,
        session_id: str,
        role: MessageRole,
        content: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> None:
        if not self.enabled:
            return

        now = datetime.now(UTC)
        message_id = f"{int(now.timestamp() * 1000):013d}-{uuid4().hex}"
        item: dict[str, object] = {
            "session_id": session_id,
            "message_id": message_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "created_at": now.isoformat(),
        }
        if input_tokens:
            item["input_tokens"] = input_tokens
        if output_tokens:
            item["output_tokens"] = output_tokens

        self._conversations_table.put_item(Item=item)  # type: ignore[union-attr]

    def load_recent_messages(self, session_id: str, limit: int = 8) -> list[ConversationTurn]:
        if not self.enabled:
            return []

        response = self._conversations_table.query(  # type: ignore[union-attr]
            KeyConditionExpression=Key("session_id").eq(session_id),
            Limit=limit,
            ScanIndexForward=False,
        )
        items = list(reversed(response.get("Items", [])))
        turns: list[ConversationTurn] = []
        for item in items:
            role = item.get("role")
            content = item.get("content")
            message_id = item.get("message_id")
            if not isinstance(role, str) or not isinstance(content, str) or not isinstance(message_id, str):
                continue
            turns.append(
                ConversationTurn(
                    role=role,  # type: ignore[arg-type]
                    content=content,
                    created_at=str(item.get("created_at", "")),
                    message_id=message_id,
                )
            )
        return turns

    @staticmethod
    def render_history(messages: list[ConversationTurn]) -> str:
        if not messages:
            return ""

        lines: list[str] = []
        for message in messages:
            prefix = "User" if message.role == "user" else "Assistant"
            lines.append(f"{prefix}: {message.content}")
        return "Conversation history:\n" + "\n".join(lines)
