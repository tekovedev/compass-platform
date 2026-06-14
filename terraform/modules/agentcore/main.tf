data "aws_caller_identity" "current" {}

locals {
  name       = "${var.project_name}-agent-${var.environment}"
  kb_arn     = "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:knowledge-base/${var.knowledge_base_id}"
  foundation = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.llm_model_id}"
  image_uri  = "${aws_ecr_repository.agent.repository_url}:${var.image_tag}"
}

# ------------------------------------------------------------
# ECR repository for the agent container image
# ------------------------------------------------------------
resource "aws_ecr_repository" "agent" {
  name                 = local.name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# ------------------------------------------------------------
# Execution role assumed by the AgentCore runtime
# ------------------------------------------------------------
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "runtime" {
  # Pull the agent image from ECR
  statement {
    sid       = "EcrAuth"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
  statement {
    sid       = "EcrPull"
    effect    = "Allow"
    actions   = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
    resources = [aws_ecr_repository.agent.arn]
  }

  # Invoke the foundation model (Nova) for generation
  statement {
    sid       = "InvokeModel"
    effect    = "Allow"
    actions   = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = [local.foundation]
  }

  # Retrieve from the Knowledge Base (KB-as-tool)
  statement {
    sid       = "RetrieveKb"
    effect    = "Allow"
    actions   = ["bedrock:Retrieve"]
    resources = [local.kb_arn]
  }

  # CloudWatch logs
  statement {
    sid       = "Logs"
    effect    = "Allow"
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
  }
}

resource "aws_iam_role" "runtime" {
  name               = "${local.name}-runtime"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}

resource "aws_iam_role_policy" "runtime" {
  name   = "${local.name}-runtime"
  role   = aws_iam_role.runtime.id
  policy = data.aws_iam_policy_document.runtime.json
}

# ------------------------------------------------------------
# AgentCore Runtime
# ------------------------------------------------------------
resource "aws_bedrockagentcore_agent_runtime" "agent" {
  agent_runtime_name = replace(local.name, "-", "_")
  description        = "Tránsito Seguro agent (${var.environment})"
  role_arn           = aws_iam_role.runtime.arn

  agent_runtime_artifact {
    container_configuration {
      container_uri = local.image_uri
    }
  }

  network_configuration {
    network_mode = "PUBLIC"
  }

  environment_variables = {
    KNOWLEDGE_BASE_ID = var.knowledge_base_id
    LLM_MODEL_ID      = var.llm_model_id
    AWS_REGION        = var.aws_region
  }

  tags = var.tags
}

# ------------------------------------------------------------
# AgentCore Memory (optional — replaces the DynamoDB conversation store)
# ------------------------------------------------------------
resource "aws_bedrockagentcore_memory" "agent" {
  count                 = var.enable_memory ? 1 : 0
  name                  = replace(local.name, "-", "_")
  event_expiry_duration = var.memory_expiry_days
  tags                  = var.tags
}
