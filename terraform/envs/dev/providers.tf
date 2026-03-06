provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "compass"
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = "tekovedev/compass-platform"
      Component   = "platform-service"
    }
  }
}
