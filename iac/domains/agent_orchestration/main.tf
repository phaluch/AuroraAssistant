# Agent Orchestration Domain
# Main Bedrock agent and related resources

# IAM Role for Bedrock Agent
resource "aws_iam_role" "bedrock_agent_role" {
  name = "${var.project_name}-${var.environment}-${var.domain}-iam-bedrock-agent-exec-role"

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
    Name   = "${var.project_name}-${var.environment}-${var.domain}-iam-bedrock-agent-exec-role"
    Domain = var.domain
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
resource "aws_bedrockagent_agent" "todoist_assistant" {
  agent_name              = "${var.project_name}-${var.environment}-${var.domain}-agent-todoist-assistant"
  agent_resource_role_arn = aws_iam_role.bedrock_agent_role.arn
  foundation_model        = "amazon.nova-lite-v1:0"
  idle_session_ttl_in_seconds = 600
  description = "Backend interaction between Todoist and Bedrock Agent"

  instruction = var.agent_instruction

  tags = {
    Name   = "${var.project_name}-${var.environment}-${var.domain}-agent-todoist-assistant"
    Domain = var.domain
  }
}

# Bedrock Agent Alias
resource "aws_bedrockagent_agent_alias" "todoist_assistant" {
  agent_alias_name = "${var.project_name}-${var.environment}-${var.domain}-agent-alias-todoist-assistant-v2"
  agent_id        = aws_bedrockagent_agent.todoist_assistant.agent_id
  description     = "Alias for Todoist Assistant Agent"
  

  tags = {
    Name   = "${var.project_name}-${var.environment}-${var.domain}-agent-alias-todoist-assistant-v2"
    Domain = var.domain
  }
}

# Bedrock Agent Action Group
resource "aws_bedrockagent_agent_action_group" "todoist_tool" {
  action_group_name = "todoist_tool"
  agent_id      = aws_bedrockagent_agent.todoist_assistant.agent_id
  agent_version = "DRAFT"
  description      = "Tools to interact with Todoist API"

  action_group_executor {
    lambda = var.todoist_lambda_arn
  }

  api_schema {
    payload = var.todoist_api_schema
  }

}