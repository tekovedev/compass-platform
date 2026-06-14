# Bedrock Guardrails
output "guardrail_id" {
  description = "Managed Bedrock guardrail ID"
  value       = module.bedrock_guardrails.guardrail_id
}

# AgentCore Runtime (null when disabled)
output "agentcore_runtime_arn" {
  description = "ARN of the AgentCore runtime"
  value       = var.enable_agentcore ? module.agentcore[0].agent_runtime_arn : null
}

output "agentcore_ecr_repository_url" {
  description = "ECR repo for the agent image"
  value       = var.enable_agentcore ? module.agentcore[0].ecr_repository_url : null
}

output "guardrail_arn" {
  description = "Managed Bedrock guardrail ARN"
  value       = module.bedrock_guardrails.guardrail_arn
}

output "guardrail_version" {
  description = "Managed Bedrock guardrail version used by the app"
  value       = module.bedrock_guardrails.guardrail_version
}

# ECS Service
output "service_name" {
  description = "Name of the ECS service"
  value       = module.ecs_service.service_name
}

output "service_arn" {
  description = "ARN of the ECS service"
  value       = module.ecs_service.service_arn
}

output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = module.ecs_service.task_definition_arn
}

output "task_definition_revision" {
  description = "Revision of the task definition"
  value       = module.ecs_service.task_definition_revision
}

# Container Image
output "image_uri" {
  description = "Full URI of the deployed image"
  value       = "${data.aws_ecr_repository.platform.repository_url}:${var.image_tag}"
}

# IAM Roles
output "task_role_arn" {
  description = "ARN of the task IAM role"
  value       = module.ecs_service.task_role_arn
}

output "task_execution_role_arn" {
  description = "ARN of the task execution IAM role"
  value       = module.ecs_service.task_execution_role_arn
}

# Security
output "security_group_id" {
  description = "ID of the ECS service security group"
  value       = module.ecs_service.security_group_id
}

# Cluster Info
output "cluster_name" {
  description = "Name of the ECS cluster"
  value       = data.aws_ecs_cluster.main.cluster_name
}

output "cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = data.aws_ecs_cluster.main.arn
}
