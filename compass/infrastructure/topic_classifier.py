from __future__ import annotations

import json
import logging

import boto3

from compass.config import settings
from compass.infrastructure.prompt_loader import load_prompt, render_prompt

logger = logging.getLogger(__name__)

OFF_TOPIC_ANSWER = (
    "Soy Tránsito Seguro, un asistente especializado en leyes de tránsito de Bolivia. "
    "No puedo ayudarte con ese tema, pero con gusto respondo preguntas sobre el "
    "Código de Tránsito — como multas, licencias, accidentes, o normativa vial. "
    "¿Tienes alguna consulta sobre tránsito?"
)


def is_traffic_law_query(query: str) -> bool:
    """Return True if the query is related to Bolivian traffic law.

    Falls back to True on any error so the agent still runs rather than
    silently dropping a valid question.
    """
    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    try:
        response = client.invoke_model(
            modelId=settings.query_expansion_model_id,
            body=json.dumps({
                "system": [{"text": load_prompt("guardrails/classifier/system.md")}],
                "messages": [{"role": "user", "content": [{"text": render_prompt("guardrails/classifier/user.md", question=query)}]}],
                "inferenceConfig": {"maxTokens": 5},
            }),
        )
        result = json.loads(response["body"].read())
        text = result["output"]["message"]["content"][0]["text"].strip().lower()
        logger.info("Topic classifier response for %r: %r", query, text)
        return text.startswith("yes")
    except Exception:
        logger.warning("Topic classifier failed, allowing query through", exc_info=True)
        return True
