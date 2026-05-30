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


class QuotaExceeded(Exception):
    def __init__(self, user_id: str, limit: int, used: int) -> None:
        self.user_id = user_id
        self.limit = limit
        self.used = used
        super().__init__(f"Monthly token quota exceeded for user {user_id}: {used}/{limit}")
