# Environment Configuration
aws_region  = "us-east-1"
environment = "dev"

# ECS Task Configuration
cpu            = 256
memory         = 512
desired_count  = 1  # Set to 0 to stop the service, 1+ to run
container_port = 8000
image_tag      = "dev-latest"  # Will be overridden by CI/CD with CalVer tag

# Environment Variables
environment_variables = {
  ENVIRONMENT        = "dev"
  LOG_LEVEL          = "INFO"
  AWS_REGION         = "us-east-1"
  
  # Bedrock Configuration
  EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
  LLM_MODEL_ID       = "amazon.nova-pro-v1:0"
  
  # Note: KNOWLEDGE_BASE_ID is set dynamically from terraform remote state
  # See main.tf for the actual value from compass-infra-tf outputs
}

# Secrets (optional - add ARNs from AWS Secrets Manager or Parameter Store)
# secrets = {
#   DATABASE_URL = "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:compass/dev/db-url-XXXXX"
#   API_KEY      = "arn:aws:ssm:us-east-1:ACCOUNT_ID:parameter/compass/dev/api-key"
# }

# Auto Scaling
enable_autoscaling        = false  # Enable when ready for production
autoscaling_min_capacity  = 1
autoscaling_max_capacity  = 4
autoscaling_cpu_target    = 70
autoscaling_memory_target = 80

# Debugging
enable_ecs_exec = true  # Allows running commands inside containers with 'aws ecs execute-command'
