locals {
  guardrail_name = coalesce(var.name, "${var.project_name}-${var.environment}")
}

resource "aws_bedrock_guardrail" "this" {
  count = var.enabled ? 1 : 0

  name                     = local.guardrail_name
  description              = var.description
  blocked_input_messaging  = var.blocked_input_messaging
  blocked_outputs_messaging = var.blocked_outputs_messaging

  dynamic "content_policy_config" {
    for_each = length(var.content_filters) > 0 ? [1] : []
    content {
      dynamic "filters_config" {
        for_each = var.content_filters
        content {
          type            = filters_config.value.type
          input_strength  = filters_config.value.input_strength
          output_strength = filters_config.value.output_strength
        }
      }
    }
  }

  dynamic "topic_policy_config" {
    for_each = length(var.denied_topics) > 0 ? [1] : []
    content {
      dynamic "topics_config" {
        for_each = var.denied_topics
        content {
          name       = topics_config.value.name
          definition = topics_config.value.definition
          examples   = topics_config.value.examples
          type       = "DENY"
        }
      }
    }
  }

  tags = merge(var.tags, {
    Name = local.guardrail_name
  })
}

resource "aws_bedrock_guardrail_version" "this" {
  count = var.enabled && var.publish_version ? 1 : 0

  guardrail_arn = aws_bedrock_guardrail.this[0].guardrail_arn
  description   = "Published version for ${local.guardrail_name}"
  skip_destroy  = true
}
