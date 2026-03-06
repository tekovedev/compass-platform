locals {
  common_tags = {
    Project     = "compass"
    Environment = var.environment
    ManagedBy   = "terraform"
    Repository  = "tekovedev/compass-platform"
    Component   = "platform-service"
  }
}

# ------------------------------------------------------------
# Module: ECS Service for compass-platform
# Python FastAPI backend
# ------------------------------------------------------------
module "ecs_service" {
  source = "../../modules/ecs_service"

  # General
  environment   = var.environment
  project_name  = "compass-platform"
  
  # Data sources (from infrastructure)
  vpc_id                = data.aws_vpc.main.id
  subnet_ids            = data.aws_subnets.private.ids
  alb_security_group_id = data.aws_security_group.alb.id
  alb_target_group_arn  = data.aws_lb_target_group.main.arn
  ecs_cluster_id        = data.aws_ecs_cluster.main.id
  ecs_cluster_name      = data.aws_ecs_cluster.main.cluster_name
  ecr_repository_url    = data.aws_ecr_repository.platform.repository_url
  log_group_name        = data.aws_cloudwatch_log_group.ecs.name
  log_group_arn         = data.aws_cloudwatch_log_group.ecs.arn
  aws_region            = data.aws_region.current.id

  # ECS Task Configuration
  cpu            = var.cpu
  memory         = var.memory
  desired_count  = var.desired_count
  container_port = var.container_port
  image_tag      = var.image_tag

  # Environment Variables & Secrets
  environment_variables = var.environment_variables
  secrets               = var.secrets

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
