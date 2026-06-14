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

logging.basicConfig(level=logging.INFO)
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
    if not prompt:
        return {"answer": "Por favor escribe una pregunta.", "sources": []}

    reply = run_turn(_agent, prompt)
    return {"answer": reply.answer, "sources": reply.sources}


if __name__ == "__main__":
    app.run()
