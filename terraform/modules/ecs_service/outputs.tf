# ECS Service
output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.platform.name
}

output "service_arn" {
  description = "ARN of the ECS service"
  value       = aws_ecs_service.platform.id
}

output "service_id" {
  description = "ID of the ECS service"
  value       = aws_ecs_service.platform.id
}

# Task Definition
output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = aws_ecs_task_definition.platform.arn
}

output "task_definition_family" {
  description = "Family of the task definition"
  value       = aws_ecs_task_definition.platform.family
}

output "task_definition_revision" {
  description = "Revision of the task definition"
  value       = aws_ecs_task_definition.platform.revision
}

# IAM Roles
output "task_role_arn" {
  description = "ARN of the task IAM role"
  value       = aws_iam_role.task.arn
}

output "task_role_name" {
  description = "Name of the task IAM role"
  value       = aws_iam_role.task.name
}

output "task_execution_role_arn" {
  description = "ARN of the task execution IAM role"
  value       = aws_iam_role.task_execution.arn
}

output "task_execution_role_name" {
  description = "Name of the task execution IAM role"
  value       = aws_iam_role.task_execution.name
}

# Security
output "security_group_id" {
  description = "ID of the ECS service security group"
  value       = aws_security_group.ecs_service.id
}

output "security_group_name" {
  description = "Name of the ECS service security group"
  value       = aws_security_group.ecs_service.name
}
