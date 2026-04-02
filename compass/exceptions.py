from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    action: str
    blocked: bool
    message: str
    action_reason: str | None = None


class GuardrailViolation(Exception):
    def __init__(self, source: str, result: GuardrailResult) -> None:
        self.source = source
        self.result = result
        super().__init__(
            f"Guardrail {source} violation: {result.message}"
        )
