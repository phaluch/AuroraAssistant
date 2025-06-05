# Agent Orchestration Domain
# Main Bedrock agent and related resources

# IAM Role for Bedrock Agent
resource "aws_iam_role" "bedrock_agent_role" {
  name = "aurora-${var.environment}-ao-iam-bedrock-agent-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = var.aws_account_id
          }
          ArnLike = {
            "AWS:SourceArn" = "arn:aws:bedrock:${var.aws_region}:${var.aws_account_id}:agent/*"
          }
        }
      }
    ]
  })

  tags = {
    Name   = "aurora-${var.environment}-ao-iam-bedrock-agent-exec-role"
    Domain = "agent-orchestration"
  }
}

# Inline policy for Bedrock foundation models
resource "aws_iam_role_policy" "bedrock_foundation_model_policy" {
  name = "bedrock-foundation-model-policy"
  role = aws_iam_role.bedrock_agent_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/*"
        ]
      }
    ]
  })
}

# Policy attachment for Lambda invocation (needed to call action group Lambdas)
resource "aws_iam_role_policy" "bedrock_lambda_invoke_policy" {
  name = "bedrock-lambda-invoke-policy"
  role = aws_iam_role.bedrock_agent_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          var.todoist_lambda_arn
        ]
      }
    ]
  })
}

# Bedrock Agent
resource "aws_bedrockagent_agent" "main_agent" {
  agent_name              = "aurora-${var.environment}-ao-agent-todoist-assistant"
  agent_resource_role_arn = aws_iam_role.bedrock_agent_role.arn
  foundation_model        = "amazon.nova-lite-v1:0"
  idle_session_ttl_in_seconds = 600
  description = "aurora project agent"

  instruction = var.agent_instruction

  tags = {
    Name   = "aurora-${var.environment}-ao-agent-todoist-assistant"
    Domain = "agent-orchestration"
  }
}

# Bedrock Agent Action Group
resource "aws_bedrockagent_agent_action_group" "todoist_tool" {
  action_group_name = "todoist-tool"
  agent_id         = aws_bedrockagent_agent.main_agent.agent_id
  agent_version    = "DRAFT"
  description      = "tools to interact with todoist"

  action_group_executor {
    lambda = var.todoist_lambda_arn
  }

  api_schema {
    payload = var.todoist_api_schema
  }
}