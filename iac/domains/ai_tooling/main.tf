# AI Tooling Domain
# Lambda functions that serve as Bedrock agent tools

# IAM Role for Todoist Lambda
resource "aws_iam_role" "todoist_lambda_role" {
  name = "aurora-${var.environment}-ait-iam-todoist-tool-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "aurora-${var.environment}-ait-iam-todoist-tool-lambda-exec-role"
    domain      = "ai-tooling"
  }
}

# Attach AWS managed policies
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.todoist_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "secrets_manager_read_write" {
  role       = aws_iam_role.todoist_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_role_policy_attachment" "bedrock_full_access" {
  role       = aws_iam_role.todoist_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}

# Create deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = var.lambda_source_file
  output_path = "${path.module}/deployment.zip"
}

# Lambda function
resource "aws_lambda_function" "todoist_tool" {
  function_name = "aurora-${var.environment}-ait-lambda-todoist-tool"
  role         = aws_iam_role.todoist_lambda_role.arn
  handler      = "lambda_function.lambda_handler"
  runtime      = "python3.12"
  timeout      = 60
  memory_size  = 128

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TODOIST_SECRET_NAME = var.todoist_secret_name
    }
  }

  layers = var.lambda_layers

  tags = {
    Name        = "aurora-${var.environment}-ait-lambda-todoist-tool"
    environment = var.environment
    domain      = "ai-tooling"
    managed-by  = "terraform"
  }
}

# Lambda permission for Bedrock agent
resource "aws_lambda_permission" "allow_bedrock" {
  statement_id  = "AllowExecutionFromBedrock"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.todoist_tool.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = var.bedrock_agent_arn
}