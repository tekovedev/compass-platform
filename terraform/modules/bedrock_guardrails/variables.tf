variable "project_name" {
  description = "Project name used for naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "enabled" {
  description = "Whether to create and manage the Bedrock guardrail"
  type        = bool
  default     = false
}

variable "name" {
  description = "Optional explicit Bedrock guardrail name"
  type        = string
  default     = null
}

variable "description" {
  description = "Description for the Bedrock guardrail"
  type        = string
  default     = "Managed Bedrock guardrails for Compass platform"
}

variable "blocked_input_messaging" {
  description = "Message shown when an input is blocked"
  type        = string
  default     = "Sorry, I can't help with that request."
}

variable "blocked_outputs_messaging" {
  description = "Message shown when an output is blocked"
  type        = string
  default     = "Sorry, I can't provide that answer."
}

variable "publish_version" {
  description = "Whether to publish a numbered Bedrock guardrail version instead of using DRAFT"
  type        = bool
  default     = false
}

variable "content_filters" {
  description = "Content policy filters to configure on the guardrail"
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

variable "denied_topics" {
  description = "Topics the model should refuse to discuss"
  type = list(object({
    name       = string
    definition = string
    examples   = list(string)
  }))
  default = []
}

variable "tags" {
  description = "Tags to apply to the guardrail resources"
  type        = map(string)
  default     = {}
}
