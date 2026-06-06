locals {
  common_tags = {
    Project     = "compass"
    Environment = var.environment
    ManagedBy   = "terraform"
    Repository  = "tekovedev/compass-platform"
    Component   = "platform-service"
  }

  guardrail_prompts_dir             = abspath("${path.root}/../../prompts/guardrails")
  guardrail_blocked_input_message   = try(trimspace(file("${local.guardrail_prompts_dir}/blocked_input.txt")), var.guardrail_blocked_input_message)
  guardrail_blocked_output_message  = try(trimspace(file("${local.guardrail_prompts_dir}/blocked_output.txt")), var.guardrail_blocked_output_message)
  guardrail_denied_topics_from_file = try(jsondecode(file("${local.guardrail_prompts_dir}/denied_topics.json")), [])
}

# ------------------------------------------------------------
# Module: Bedrock Guardrails
# Optional safety and prompt protections managed with the backend
# ------------------------------------------------------------
module "bedrock_guardrails" {
  source = "../../modules/bedrock_guardrails"

  project_name              = "compass-platform"
  environment               = var.environment
  enabled                   = var.enable_guardrails
  name                      = var.guardrail_name
  description               = var.guardrail_description
  blocked_input_messaging   = local.guardrail_blocked_input_message
  blocked_outputs_messaging = local.guardrail_blocked_output_message
  publish_version           = var.guardrail_publish_version
  content_filters           = var.guardrail_content_filters
  denied_topics             = length(var.guardrail_denied_topics) > 0 ? var.guardrail_denied_topics : local.guardrail_denied_topics_from_file

  tags = local.common_tags
}

# ------------------------------------------------------------
# Module: ECS Service for compass-platform
# Python FastAPI backend
# ------------------------------------------------------------
module "ecs_service" {
  source = "../../modules/ecs_service"

  # General
  environment  = var.environment
  project_name = "compass-platform"

  # Data sources (from infrastructure)
  vpc_id                = data.aws_vpc.main.id
  subnet_ids            = data.aws_subnets.public.ids
  assign_public_ip      = true
  alb_security_group_id = data.aws_security_group.alb.id
  alb_target_group_arn  = data.aws_lb_target_group.main.arn
  ecs_cluster_id        = data.aws_ecs_cluster.main.id
  ecs_cluster_name      = data.aws_ecs_cluster.main.cluster_name
  ecr_repository_url    = data.aws_ecr_repository.platform.repository_url
  log_group_name        = data.aws_cloudwatch_log_group.ecs.name
  log_group_arn         = data.aws_cloudwatch_log_group.ecs.arn
  aws_region            = var.aws_region

  # ECS Task Configuration
  cpu            = var.cpu
  memory         = var.memory
  desired_count  = var.desired_count
  container_port = var.container_port
  image_tag      = var.image_tag

  # AWS Resources
  knowledge_base_arn           = data.terraform_remote_state.knowledge_hub.outputs.knowledge_base_arn
  chat_sessions_table_arn      = data.terraform_remote_state.infra.outputs.chat_sessions_table_arn
  chat_conversations_table_arn = data.terraform_remote_state.infra.outputs.chat_conversations_table_arn
  chat_monthly_usage_table_arn = data.terraform_remote_state.infra.outputs.chat_monthly_usage_table_arn

  # Environment Variables & Secrets
  environment_variables = merge(
    var.environment_variables,
    {
      # Dynamically inject shared platform settings from infra remote state
      KNOWLEDGE_BASE_ID             = data.terraform_remote_state.knowledge_hub.outputs.knowledge_base_id
      COGNITO_USER_POOL_ID          = data.terraform_remote_state.infra.outputs.cognito_user_pool_id
      COGNITO_CLIENT_ID             = data.terraform_remote_state.infra.outputs.cognito_app_client_id
      COGNITO_REGION                = data.terraform_remote_state.infra.outputs.aws_region
      COGNITO_DOMAIN                = data.terraform_remote_state.infra.outputs.cognito_hosted_ui_domain
      CHAT_SESSIONS_TABLE_NAME      = data.terraform_remote_state.infra.outputs.chat_sessions_table_name
      CHAT_CONVERSATIONS_TABLE_NAME = data.terraform_remote_state.infra.outputs.chat_conversations_table_name
      CHAT_MONTHLY_USAGE_TABLE_NAME = data.terraform_remote_state.infra.outputs.chat_monthly_usage_table_name
      MONTHLY_TOKEN_LIMIT           = "200000"
      GUARDRAIL_ID                  = module.bedrock_guardrails.guardrail_id
      GUARDRAIL_VERSION             = module.bedrock_guardrails.guardrail_version
    }
  )
  secrets = var.secrets

  # Auto Scaling
  enable_autoscaling        = var.enable_autoscaling
  autoscaling_min_capacity  = var.autoscaling_min_capacity
  autoscaling_max_capacity  = var.autoscaling_max_capacity
  autoscaling_cpu_target    = var.autoscaling_cpu_target
  autoscaling_memory_target = var.autoscaling_memory_target

  # Debugging
  enable_ecs_exec = var.enable_ecs_exec

  # Tags
  tags = local.common_tags
}
