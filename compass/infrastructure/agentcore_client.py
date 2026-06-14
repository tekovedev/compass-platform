"""Client for the Tránsito Seguro agent running on Bedrock AgentCore Runtime.

The FastAPI service delegates answer generation to the deployed agent: the agent
decides whether to consult the Knowledge Base (KB-as-tool) and returns the answer
plus any sources it actually retrieved.
"""

from __future__ import annotations

import json
import logging

import boto3

from compass.config import settings

logger = logging.getLogger(__name__)


def _session_id(session_id: str | None) -> str:
    """AgentCore requires a runtime session id of 33-256 chars."""
    base = session_id or "anon"
    return base if len(base) >= 33 else base.ljust(33, "0")


def _build_prompt(query: str, history: str | None) -> str:
    """Fold conversation history into the prompt so multi-turn context survives.

    The agent is invoked statelessly; prior turns are passed as context and the
    latest question is clearly marked so the agent answers it.
    """
    if history:
        return f"{history}\n\nNueva pregunta del usuario: {query}"
    return query


def invoke_agent(
    query: str,
    session_id: str | None = None,
    history: str | None = None,
) -> tuple[str, list[str]]:
    """Invoke the AgentCore runtime and return (answer, sources)."""
    if not settings.agentcore_runtime_arn:
        raise RuntimeError("AGENTCORE_RUNTIME_ARN is not configured")

    client = boto3.client("bedrock-agentcore", region_name=settings.aws_region)
    response = client.invoke_agent_runtime(
        agentRuntimeArn=settings.agentcore_runtime_arn,
        runtimeSessionId=_session_id(session_id),
        payload=json.dumps({"prompt": _build_prompt(query, history)}).encode(),
        contentType="application/json",
        accept="application/json",
    )
    data = json.loads(response["response"].read())
    return data.get("answer", ""), data.get("sources", [])
