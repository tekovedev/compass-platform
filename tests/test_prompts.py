"""Tests for centralized prompt loading."""

from compass.infrastructure.prompt_loader import load_json_prompt, load_prompt


def test_load_system_prompt_from_prompts_folder():
    prompt = load_prompt("rag/system.md")
    assert "tránsito seguro" in prompt.lower()
    assert "bolivia" in prompt.lower()


def test_load_guardrail_topics_json():
    topics = load_json_prompt("guardrails/denied_topics.json")
    assert isinstance(topics, list)
