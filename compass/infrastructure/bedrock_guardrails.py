from __future__ import annotations

import logging

import boto3

from compass.config import settings
from compass.exceptions import GuardrailResult, GuardrailViolation

logger = logging.getLogger(__name__)


def apply_guardrail(text: str, source: str) -> GuardrailResult:
    """Call the Bedrock ApplyGuardrail API.

    Args:
        text: The content to evaluate.
        source: "INPUT" or "OUTPUT".

    Returns:
        GuardrailResult with the guardrail action.

    Raises:
        GuardrailViolation: If the guardrail blocks the content.
    """
    guardrail_id = (settings.guardrail_id or "").strip()
    if not guardrail_id:
        return GuardrailResult(action="NONE", blocked=False, message="")

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    response = client.apply_guardrail(
        guardrailIdentifier=guardrail_id,
        guardrailVersion=settings.guardrail_version,
        source=source,
        content=[{"text": {"text": text}}],
    )

    action = response.get("action", "NONE")
    blocked = action == "GUARDRAIL_INTERVENED"

    outputs = response.get("outputs", [])
    message = outputs[0]["text"] if outputs else ""

    assessments = response.get("assessments", [])
    action_reason = None
    if assessments:
        first = assessments[0]
        for policy_type in ("contentPolicy", "topicPolicy", "wordPolicy", "sensitiveInformationPolicy"):
            policy = first.get(policy_type)
            if policy:
                action_reason = policy_type
                break

    result = GuardrailResult(
        action=action,
        blocked=blocked,
        message=message,
        action_reason=action_reason,
    )

    logger.info(
        "Guardrail check source=%s action=%s blocked=%s reason=%s",
        source, action, blocked, action_reason,
    )

    if blocked:
        raise GuardrailViolation(source=source, result=result)

    return result


def check_input(text: str) -> GuardrailResult:
    return apply_guardrail(text, source="INPUT")


def check_output(text: str) -> GuardrailResult:
    return apply_guardrail(text, source="OUTPUT")
