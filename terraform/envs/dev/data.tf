# Data sources to reference existing infrastructure created by compass-infra-tf

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# VPC and Networking
data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["compass-vpc-${var.environment}"]
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }

  filter {
    name   = "tag:Type"
    values = ["public"]
  }
}

# ECS Cluster
data "aws_ecs_cluster" "main" {
  cluster_name = "compass-cluster-${var.environment}"
}

# Application Load Balancer
data "aws_lb" "main" {
  tags = {
    Name = "compass-alb-${var.environment}"
  }
}

data "aws_lb_target_group" "main" {
  tags = {
    Name = "compass-default-tg-${var.environment}"
  }
}

# ALB Security Group (para permitir tráfico desde ALB)
data "aws_security_group" "alb" {
  filter {
    name   = "tag:Name"
    values = ["compass-alb-sg-${var.environment}"]
  }

  vpc_id = data.aws_vpc.main.id
}

# ECR Repository
data "aws_ecr_repository" "platform" {
  name = "compass-platform-${var.environment}"
}

# CloudWatch Log Group (creado por el módulo ecs_cluster)
data "aws_cloudwatch_log_group" "ecs" {
  name = "/ecs/compass-${var.environment}"
}
