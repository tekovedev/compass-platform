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
