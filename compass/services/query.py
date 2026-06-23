from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from compass.infrastructure.bedrock_guardrails import check_input, check_output
from compass.infrastructure.agentcore_client import invoke_agent
from compass.infrastructure.conversation_store import ConversationStore
from compass.infrastructure.token_quota_store import TokenQuotaStore

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    answer: str
    sources: list[str]
    session_id: str
    input_tokens: int = 0
    output_tokens: int = 0


class QueryService:
    def __init__(
        self,
        conversation_store: ConversationStore | None = None,
        quota_store: TokenQuotaStore | None = None,
    ) -> None:
        self.conversation_store = conversation_store or ConversationStore()
        self.quota_store = quota_store or TokenQuotaStore()

    async def execute(
        self,
        query: str,
        user_id: str,
        session_id: str | None = None,
    ) -> QueryResult:
        """Run the full query pipeline: guardrails -> AgentCore -> guardrails.

        Retrieval and generation are delegated to the AgentCore runtime, which
        decides whether to consult the Knowledge Base. Auth, quota, guardrails
        and conversation persistence stay in this service.

        Lets GuardrailViolation propagate to the caller.
        """
        logger.info("[QUERY] guardrails input check | user_id=%s", user_id)
        await asyncio.to_thread(check_input, query)

        estimated_prompt_tokens = max(1, len(query) // 4)
        logger.info("[QUERY] quota check | user_id=%s | estimated_tokens=%d", user_id, estimated_prompt_tokens)
        await asyncio.to_thread(self.quota_store.ensure_quota, user_id, estimated_prompt_tokens)

        resolved_session_id = await asyncio.to_thread(
            self.conversation_store.upsert_session,
            user_id,
            session_id,
            query[:80],
        )
        logger.info("[QUERY] session resolved | session_id=%s", resolved_session_id)

        history = await asyncio.to_thread(
            self.conversation_store.load_recent_messages,
            resolved_session_id,
            8,
        )
        history_text = ConversationStore.render_history(history)
        logger.debug("[QUERY] conversation history (%d messages):\n%s", len(history), history_text or "(none)")

        await asyncio.to_thread(
            self.conversation_store.append_message,
            user_id,
            resolved_session_id,
            "user",
            query,
        )

        logger.info("[QUERY] invoking AgentCore | session_id=%s | query=%r", resolved_session_id, query)
        answer, sources = await asyncio.to_thread(
            invoke_agent,
            query,
            resolved_session_id,
            history_text or None,
        )
        logger.info("[QUERY] AgentCore response | sources=%s | answer=%r", sources, answer)

        logger.info("[QUERY] guardrails output check")
        await asyncio.to_thread(check_output, answer)

        # AgentCore does not return token usage; estimate from text length.
        consumed_tokens = max(1, len(query) // 4) + max(1, len(answer) // 4)
        await asyncio.to_thread(self.quota_store.consume, user_id, consumed_tokens)

        await asyncio.to_thread(
            self.conversation_store.append_message,
            user_id,
            resolved_session_id,
            "assistant",
            answer,
        )
        await asyncio.to_thread(self.conversation_store.touch_session, user_id, resolved_session_id)

        return QueryResult(
            answer=answer,
            sources=sources,
            session_id=resolved_session_id,
        )
