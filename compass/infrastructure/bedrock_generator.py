from __future__ import annotations

import json

import boto3

from compass.config import settings
from compass.infrastructure.prompt_loader import load_prompt, render_prompt


def generate(query: str, context_chunks: list[str]) -> str:
    """Generate an answer using Bedrock with prompts loaded from the shared prompts folder."""
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant context was retrieved."
    system_prompt = load_prompt("rag/system.txt")
    user_prompt = render_prompt("rag/user.txt", context=context, question=query)

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
    return result["output"]["message"]["content"][0]["text"]
