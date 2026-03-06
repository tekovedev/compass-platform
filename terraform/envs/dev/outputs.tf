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
