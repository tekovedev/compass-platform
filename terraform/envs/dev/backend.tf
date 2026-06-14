terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.50.0" # aws_bedrockagentcore_agent_runtime / _memory
    }
  }

  backend "s3" {
    bucket       = "tekove-compass-tf-states-dev"
    key          = "compass/platform/dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
