from __future__ import annotations

import asyncio
from dataclasses import dataclass

from compass.infrastructure.bedrock_guardrails import check_input, check_output
from compass.infrastructure.bedrock_retriever import retrieve
from compass.infrastructure.bedrock_generator import generate


@dataclass
class QueryResult:
    answer: str
    sources: list[str]


class QueryService:
    async def execute(self, query: str, top_k: int = 5) -> QueryResult:
        """Run the full query pipeline: guardrails -> retrieve -> generate -> guardrails.

        Lets GuardrailViolation propagate to the caller.
        """
        await asyncio.to_thread(check_input, query)
        context_chunks = await asyncio.to_thread(retrieve, query, top_k)
        answer = await asyncio.to_thread(generate, query, context_chunks)
        await asyncio.to_thread(check_output, answer)
        return QueryResult(answer=answer, sources=context_chunks)
