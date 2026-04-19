"""Tests for centralized prompt loading."""

from compass.infrastructure.prompt_loader import load_json_prompt, load_prompt, render_prompt


def test_load_system_prompt_from_prompts_folder():
    prompt = load_prompt("rag/system.txt")
    assert "helpful assistant" in prompt.lower()


def test_render_user_prompt_template():
    rendered = render_prompt("rag/user.txt", context="ctx", question="What is the rule?")
    assert "ctx" in rendered
    assert "What is the rule?" in rendered


def test_load_guardrail_topics_json():
    topics = load_json_prompt("guardrails/denied_topics.json")
    assert isinstance(topics, list)
