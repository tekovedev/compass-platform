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

# AgentCore (parallel agent runtime — disabled by default until the image is built)
variable "enable_agentcore" {
  description = "Create the AgentCore runtime for the Strands agent"
  type        = bool
  default     = false
}

variable "agent_image_tag" {
  description = "Container image tag for the AgentCore runtime"
  type        = string
  default     = "latest"
}

variable "agent_enable_memory" {
  description = "Create an AgentCore Memory store for the agent"
  type        = bool
  default     = false
}

# Bedrock Guardrails
variable "enable_guardrails" {
  description = "Whether the backend Terraform should create and manage a Bedrock guardrail"
  type        = bool
  default     = false
}

variable "guardrail_name" {
  description = "Optional explicit name for the Bedrock guardrail"
  type        = string
  default     = null
}

variable "guardrail_description" {
  description = "Description for the Bedrock guardrail"
  type        = string
  default     = "Compass backend guardrails for legal assistant queries"
}

variable "guardrail_blocked_input_message" {
  description = "Message returned when a user input is blocked"
  type        = string
  default     = "Sorry, I can't help with that request."
}

variable "guardrail_blocked_output_message" {
  description = "Message returned when a model response is blocked"
  type        = string
  default     = "Sorry, I can't provide that answer."
}

variable "guardrail_publish_version" {
  description = "Publish a numbered Bedrock guardrail version instead of using DRAFT"
  type        = bool
  default     = false
}

variable "guardrail_content_filters" {
  description = "Content filters for the managed Bedrock guardrail"
  type = list(object({
    type            = string
    input_strength  = string
    output_strength = string
  }))
  default = [
    {
      type            = "PROMPT_ATTACK"
      input_strength  = "HIGH"
      output_strength = "NONE"
    },
    {
      type            = "MISCONDUCT"
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
    },
    {
      type            = "HATE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    },
    {
      type            = "SEXUAL"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    },
    {
      type            = "VIOLENCE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
  ]
}

variable "guardrail_denied_topics" {
  description = "Topics the assistant should refuse via the Bedrock guardrail"
  type = list(object({
    name       = string
    definition = string
    examples   = list(string)
  }))
  default = []
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
