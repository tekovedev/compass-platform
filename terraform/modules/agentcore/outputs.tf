output "agent_runtime_arn" {
  description = "ARN of the AgentCore runtime"
  value       = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
}

output "agent_runtime_id" {
  description = "ID of the AgentCore runtime"
  value       = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_id
}

output "ecr_repository_url" {
  description = "ECR repository the agent image is pushed to"
  value       = aws_ecr_repository.agent.repository_url
}

output "runtime_role_arn" {
  description = "Execution role assumed by the runtime"
  value       = aws_iam_role.runtime.arn
}

output "memory_id" {
  description = "AgentCore Memory ID (null when disabled)"
  value       = var.enable_memory ? aws_bedrockagentcore_memory.agent[0].id : null
}
