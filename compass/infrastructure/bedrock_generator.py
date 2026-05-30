from __future__ import annotations

from dataclasses import dataclass
import json

import boto3

from compass.config import settings
from compass.infrastructure.prompt_loader import load_prompt, render_prompt


@dataclass(frozen=True)
class GenerationResult:
    answer: str
    input_tokens: int = 0
    output_tokens: int = 0


def generate(
    query: str,
    context_chunks: list[str],
    conversation_history: str | None = None,
) -> GenerationResult:
    """Generate an answer using Bedrock with prompts loaded from the shared prompts folder."""
    context_parts: list[str] = []
    if conversation_history:
        context_parts.append(conversation_history)
    if context_chunks:
        context_parts.append("\n\n---\n\n".join(context_chunks))

    context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context was retrieved."
    system_prompt = load_prompt("rag/system.md")
    user_prompt = render_prompt("rag/user.md", context=context, question=query)

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    response = client.invoke_model(
        modelId=settings.llm_model_id,
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": user_prompt}],
                },
            ],
            "inferenceConfig": {"maxTokens": 1024},
        }),
    )
    result = json.loads(response["body"].read())
    answer = result["output"]["message"]["content"][0]["text"]
    usage = result.get("usage") or result.get("usageMetadata") or {}

    def _usage_value(*keys: str) -> int:
        for key in keys:
            value = usage.get(key)
            if isinstance(value, int):
                return value
        return 0

    return GenerationResult(
        answer=answer,
        input_tokens=_usage_value("inputTokens", "input_tokens"),
        output_tokens=_usage_value("outputTokens", "output_tokens"),
    )
