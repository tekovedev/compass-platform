# Data source to read compass-infra-tf remote state
# This allows us to reference outputs from the infrastructure repo
data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket = "tekove-compass-tf-states-dev"
    key    = "compass/bedrock-kb/dev/terraform.tfstate"
    region = "us-east-1"
  }
}


# Data source to read compass-knowledge-hub remote state
# This is the source of truth for Bedrock Knowledge Base identifiers
data "terraform_remote_state" "knowledge_hub" {
  backend = "s3"

  config = {
    bucket = "tekove-compass-tf-states-dev"
    key    = "compass/knowledge-hub/dev/terraform.tfstate"
    region = "us-east-1"
  }
}
