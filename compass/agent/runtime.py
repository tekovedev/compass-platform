"""AgentCore Runtime entrypoint for the Tránsito Seguro agent.

`BedrockAgentCoreApp` exposes the agent as the HTTP contract AgentCore Runtime
expects (POST /invocations, GET /ping on port 8080). Run locally with:

    python -m compass.agent.runtime

and deploy the same container image to an `aws_bedrockagentcore_agent_runtime`.
"""

from __future__ import annotations

import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from compass.agent.agent import build_agent, run_turn
from compass.infrastructure.topic_classifier import OFF_TOPIC_ANSWER, is_traffic_law_query

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# Built once per runtime instance and reused across invocations.
_agent = build_agent(use_knowledge_base=True)


@app.entrypoint
def invoke(payload: dict, context: object | None = None) -> dict:
    """Handle one agent invocation.

    Expected payload: {"prompt": "<user message>"}.
    Returns {"answer": str, "sources": list[str]} — `sources` is empty when the
    model did not consult the Knowledge Base (e.g. greetings).
    """
    prompt = (payload or {}).get("prompt", "").strip()
    logger.info("[AGENT] invocation received | prompt=%r", prompt)

    if not prompt:
        logger.info("[AGENT] empty prompt — returning default message")
        return {"answer": "Por favor escribe una pregunta.", "sources": []}

    if not is_traffic_law_query(prompt):
        logger.info("[AGENT] off-topic — skipping retrieval")
        return {"answer": OFF_TOPIC_ANSWER, "sources": []}

    logger.info("[AGENT] on-topic — running agent turn")
    reply = run_turn(_agent, prompt)
    logger.info("[AGENT] answer=%r | sources=%s", reply.answer, reply.sources)
    return {"answer": reply.answer, "sources": reply.sources}


if __name__ == "__main__":
    app.run()
