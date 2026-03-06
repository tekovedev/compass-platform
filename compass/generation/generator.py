from __future__ import annotations

import json

import boto3

from compass.config import settings

SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the provided context to answer the user's "
    "question. If the context doesn't contain enough information, say so."
)


def generate(query: str, context_chunks: list[str]) -> str:
    """Generate an answer using Bedrock Claude with retrieved context."""
    context = "\n\n---\n\n".join(context_chunks)
    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    response = client.invoke_model(
        modelId=settings.llm_model_id,
        body=json.dumps({
            "system": [{"text": SYSTEM_PROMPT}],
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": f"Context:\n{context}\n\nQuestion: {query}"}],
                },
            ],
            "inferenceConfig": {"maxTokens": 1024},
        }),
    )
    result = json.loads(response["body"].read())
    return result["output"]["message"]["content"][0]["text"]
