output "guardrail_id" {
  description = "Bedrock guardrail ID"
  value       = try(aws_bedrock_guardrail.this[0].guardrail_id, "")
}

output "guardrail_arn" {
  description = "Bedrock guardrail ARN"
  value       = try(aws_bedrock_guardrail.this[0].guardrail_arn, "")
}

output "guardrail_status" {
  description = "Current Bedrock guardrail status"
  value       = try(aws_bedrock_guardrail.this[0].status, "DISABLED")
}

output "guardrail_version" {
  description = "Version for application use, DRAFT unless publish_version is enabled"
  value       = var.enabled ? (var.publish_version ? aws_bedrock_guardrail_version.this[0].version : "DRAFT") : ""
}
