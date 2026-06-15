"""Tránsito Seguro agent built on the Strands Agents SDK.

This is the framework-level definition. The Knowledge Base is registered as a
tool, so retrieval becomes a model decision rather than a fixed pipeline step.
To run *without* the KB as a tool, build the agent with `tools=[]`.
"""

from __future__ import annotations

from dataclasses import dataclass

from strands import Agent
from strands.models import BedrockModel

from compass.config import settings
from compass.infrastructure.prompt_loader import load_prompt
from compass.agent.tools import buscar_codigo_transito, buscar_con_expansion, collected_sources, reset_sources


@dataclass(frozen=True)
class AgentReply:
    answer: str
    sources: list[str]


def build_agent(*, use_knowledge_base: bool = True) -> Agent:
    """Construct the agent. Flip `use_knowledge_base` to toggle the KB tool."""
    model = BedrockModel(
        model_id=settings.llm_model_id,
        region_name=settings.aws_region,
    )
    tools = [buscar_codigo_transito, buscar_con_expansion] if use_knowledge_base else []
    system_prompt = load_prompt("agent/system.md")
    return Agent(
        model=model,
        system_prompt=system_prompt,
        tools=tools,
    )


def _extract_text(result: object) -> str:
    """Pull the assistant's text out of a Strands AgentResult."""
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        parts = [block.get("text", "") for block in message.get("content", []) if isinstance(block, dict)]
        text = "".join(parts).strip()
        if text:
            return text
    return str(result).strip()


def run_turn(agent: Agent, prompt: str) -> AgentReply:
    """Run a single user turn and capture any sources the model retrieved."""
    reset_sources()
    result = agent(prompt)
    return AgentReply(answer=_extract_text(result), sources=collected_sources())
