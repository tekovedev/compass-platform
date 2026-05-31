from __future__ import annotations

import json
import logging

import boto3

from compass.config import settings
from compass.infrastructure.prompt_loader import load_prompt, render_prompt

logger = logging.getLogger(__name__)


def expand_query(query: str) -> list[str]:
    """Expand a user query into multiple semantic search queries via Bedrock.

    Uses the query expansion prompts and Nova Lite to generate alternative
    search queries.  Falls back to the original query on any failure.
    """
    system_prompt = load_prompt("query/system.md")
    user_prompt = render_prompt("query/user.md", question=query)

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)

    try:
        response = client.invoke_model(
            modelId=settings.query_expansion_model_id,
            body=json.dumps({
                "system": [{"text": system_prompt}],
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": user_prompt}],
                    },
                ],
                "inferenceConfig": {"maxTokens": 256},
            }),
        )
        result = json.loads(response["body"].read())
        text = result["output"]["message"]["content"][0]["text"]
        logger.info("Query expander raw response: %r", text)
        # Strip markdown code fences if the model wraps the JSON
        stripped = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        queries = json.loads(stripped)
        if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
            return queries
    except Exception:
        logger.warning("Query expansion failed, using original query", exc_info=True)

    return [query]
