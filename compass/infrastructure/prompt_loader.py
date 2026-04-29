from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


@lru_cache(maxsize=None)
def load_prompt(relative_path: str) -> str:
    """Load a prompt file from the central prompts folder."""
    prompt_path = PROMPTS_DIR / relative_path
    return prompt_path.read_text(encoding="utf-8").strip()


def render_prompt(relative_path: str, **values: str) -> str:
    """Render a prompt template using Python format placeholders."""
    return load_prompt(relative_path).format(**values)


def load_json_prompt(relative_path: str) -> Any:
    """Load a JSON configuration file from the prompts folder."""
    return json.loads(load_prompt(relative_path))
