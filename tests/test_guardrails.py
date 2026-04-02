"""Tests for Bedrock Guardrails integration."""

from unittest.mock import patch, MagicMock

import pytest

from compass.exceptions import GuardrailResult, GuardrailViolation
from compass.infrastructure.bedrock_guardrails import (
    apply_guardrail,
    check_input,
    check_output,
)


# --- GuardrailResult dataclass ---

def test_guardrail_result_immutable():
    result = GuardrailResult(action="NONE", blocked=False, message="ok")
    with pytest.raises(AttributeError):
        result.action = "CHANGED"


def test_guardrail_result_defaults():
    result = GuardrailResult(action="NONE", blocked=False, message="")
    assert result.action_reason is None


# --- No-op when guardrail_id is None ---

@patch("compass.infrastructure.bedrock_guardrails.settings")
def test_noop_when_guardrail_id_none(mock_settings):
    mock_settings.guardrail_id = None
    result = check_input("anything")
    assert result.blocked is False
    assert result.action == "NONE"


@patch("compass.infrastructure.bedrock_guardrails.settings")
def test_noop_output_when_guardrail_id_none(mock_settings):
    mock_settings.guardrail_id = None
    result = check_output("anything")
    assert result.blocked is False


# --- Passing checks (GUARDRAIL_NONE) ---

@patch("compass.infrastructure.bedrock_guardrails.boto3")
@patch("compass.infrastructure.bedrock_guardrails.settings")
def test_input_passes(mock_settings, mock_boto3):
    mock_settings.guardrail_id = "abc123"
    mock_settings.guardrail_version = "DRAFT"
    mock_settings.aws_region = "us-east-1"

    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.apply_guardrail.return_value = {
        "action": "NONE",
        "outputs": [{"text": ""}],
        "assessments": [],
    }

    result = check_input("What is the speed limit?")
    assert result.blocked is False
    assert result.action == "NONE"

    mock_client.apply_guardrail.assert_called_once_with(
        guardrailIdentifier="abc123",
        guardrailVersion="DRAFT",
        source="INPUT",
        content=[{"text": {"text": "What is the speed limit?"}}],
    )


@patch("compass.infrastructure.bedrock_guardrails.boto3")
@patch("compass.infrastructure.bedrock_guardrails.settings")
def test_output_passes(mock_settings, mock_boto3):
    mock_settings.guardrail_id = "abc123"
    mock_settings.guardrail_version = "DRAFT"
    mock_settings.aws_region = "us-east-1"

    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.apply_guardrail.return_value = {
        "action": "NONE",
        "outputs": [{"text": "The speed limit is 60 km/h."}],
        "assessments": [],
    }

    result = check_output("The speed limit is 60 km/h.")
    assert result.blocked is False


# --- Blocked checks (GUARDRAIL_INTERVENED) ---

@patch("compass.infrastructure.bedrock_guardrails.boto3")
@patch("compass.infrastructure.bedrock_guardrails.settings")
def test_input_blocked_raises_violation(mock_settings, mock_boto3):
    mock_settings.guardrail_id = "abc123"
    mock_settings.guardrail_version = "DRAFT"
    mock_settings.aws_region = "us-east-1"

    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.apply_guardrail.return_value = {
        "action": "GUARDRAIL_INTERVENED",
        "outputs": [{"text": "Sorry, I cannot process this request."}],
        "assessments": [{"contentPolicy": {"filters": []}}],
    }

    with pytest.raises(GuardrailViolation) as exc_info:
        check_input("harmful content")

    assert exc_info.value.source == "INPUT"
    assert exc_info.value.result.blocked is True
    assert exc_info.value.result.message == "Sorry, I cannot process this request."
    assert exc_info.value.result.action_reason == "contentPolicy"


@patch("compass.infrastructure.bedrock_guardrails.boto3")
@patch("compass.infrastructure.bedrock_guardrails.settings")
def test_output_blocked_raises_violation(mock_settings, mock_boto3):
    mock_settings.guardrail_id = "abc123"
    mock_settings.guardrail_version = "DRAFT"
    mock_settings.aws_region = "us-east-1"

    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.apply_guardrail.return_value = {
        "action": "GUARDRAIL_INTERVENED",
        "outputs": [{"text": "Content blocked."}],
        "assessments": [{"sensitiveInformationPolicy": {"piiEntities": []}}],
    }

    with pytest.raises(GuardrailViolation) as exc_info:
        check_output("some PII content")

    assert exc_info.value.source == "OUTPUT"
    assert exc_info.value.result.blocked is True
    assert exc_info.value.result.action_reason == "sensitiveInformationPolicy"


# --- GuardrailViolation exception ---

def test_guardrail_violation_str():
    result = GuardrailResult(
        action="GUARDRAIL_INTERVENED", blocked=True, message="blocked"
    )
    exc = GuardrailViolation(source="INPUT", result=result)
    assert "INPUT" in str(exc)
    assert "blocked" in str(exc)
