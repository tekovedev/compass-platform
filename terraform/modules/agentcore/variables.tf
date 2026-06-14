variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "compass"
}

variable "environment" {
  description = "Environment name (e.g. dev, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "image_tag" {
  description = "Container image tag to deploy to the AgentCore runtime"
  type        = string
  default     = "latest"
}

variable "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID the agent retrieves from"
  type        = string
}

variable "llm_model_id" {
  description = "Bedrock model ID used by the agent"
  type        = string
  default     = "amazon.nova-pro-v1:0"
}

variable "enable_memory" {
  description = "Create an AgentCore Memory store for conversation history"
  type        = bool
  default     = false
}

variable "memory_expiry_days" {
  description = "Event expiry duration (days) for AgentCore Memory"
  type        = number
  default     = 30
}

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default     = {}
}
