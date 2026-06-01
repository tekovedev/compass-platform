from __future__ import annotations

import asyncio
from dataclasses import dataclass

from compass.infrastructure.bedrock_guardrails import check_input, check_output
from compass.infrastructure.bedrock_retriever import retrieve
from compass.infrastructure.bedrock_generator import generate
from compass.infrastructure.conversation_store import ConversationStore
from compass.infrastructure.token_quota_store import TokenQuotaStore
from compass.infrastructure.query_expander import expand_query


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
        top_k: int = 5,
    ) -> QueryResult:
        """Run the full query pipeline: guardrails -> retrieve -> generate -> guardrails.

        Lets GuardrailViolation propagate to the caller.
        """
        await asyncio.to_thread(check_input, query)
        estimated_prompt_tokens = max(1, len(query) // 4)
        await asyncio.to_thread(self.quota_store.ensure_quota, user_id, estimated_prompt_tokens)

        resolved_session_id = await asyncio.to_thread(
            self.conversation_store.upsert_session,
            user_id,
            session_id,
            query[:80],
        )

        history = await asyncio.to_thread(
            self.conversation_store.load_recent_messages,
            resolved_session_id,
            8,
        )
        history_text = ConversationStore.render_history(history)

        await asyncio.to_thread(
            self.conversation_store.append_message,
            user_id,
            resolved_session_id,
            "user",
            query,
        )

        queries = await asyncio.to_thread(expand_query, query)
        context_chunks = await asyncio.to_thread(retrieve, queries, top_k)
        generation = await asyncio.to_thread(generate, query, context_chunks, history_text or None)
        answer = generation.answer
        await asyncio.to_thread(check_output, answer)

        consumed_tokens = generation.input_tokens + generation.output_tokens
        if consumed_tokens == 0:
            consumed_tokens = max(1, len(query) // 4) + max(1, len(answer) // 4)
        await asyncio.to_thread(self.quota_store.consume, user_id, consumed_tokens)

        await asyncio.to_thread(
            self.conversation_store.append_message,
            user_id,
            resolved_session_id,
            "assistant",
            answer,
            generation.input_tokens,
            generation.output_tokens,
        )
        await asyncio.to_thread(self.conversation_store.touch_session, user_id, resolved_session_id)

        return QueryResult(
            answer=answer,
            sources=generation.sources,
            session_id=resolved_session_id,
            input_tokens=generation.input_tokens,
            output_tokens=generation.output_tokens,
        )
