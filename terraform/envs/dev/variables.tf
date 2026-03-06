# General
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

# ECS Task Configuration
variable "cpu" {
  description = "CPU units for the task (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
}

variable "memory" {
  description = "Memory for the task in MB (512, 1024, 2048, etc.)"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of tasks to run"
  type        = number
  default     = 1
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "image_tag" {
  description = "Docker image tag to deploy (commit SHA, 'latest', etc.)"
  type        = string
  default     = "latest"
}

# Environment Variables
variable "environment_variables" {
  description = "Environment variables for the container"
  type        = map(string)
  default = {
    ENVIRONMENT = "dev"
    LOG_LEVEL   = "INFO"
  }
}

variable "secrets" {
  description = "Secrets from AWS Secrets Manager or Parameter Store"
  type        = map(string)
  default     = {}
}

# Auto Scaling
variable "enable_autoscaling" {
  description = "Enable auto scaling for the service"
  type        = bool
  default     = false
}

variable "autoscaling_min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 4
}

variable "autoscaling_cpu_target" {
  description = "Target CPU utilization percentage for auto scaling"
  type        = number
  default     = 70
}

variable "autoscaling_memory_target" {
  description = "Target memory utilization percentage for auto scaling"
  type        = number
  default     = 80
}

# Debugging
variable "enable_ecs_exec" {
  description = "Enable ECS Exec for debugging (allows 'aws ecs execute-command')"
  type        = bool
  default     = true
}
