# Lambda Function Module
# iac/modules/aws_lambda_function/main.tf

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role         = aws_iam_role.lambda_execution.arn
  handler      = var.handler
  runtime      = var.runtime
  timeout      = var.timeout
  memory_size  = var.memory_size
  
  # For imported functions, use dummy zip to satisfy Terraform requirements
  # The actual code will remain unchanged until you deploy new code
  filename         = var.filename != null ? var.filename : "${path.module}/dummy.zip"
  source_code_hash = var.filename != null ? var.source_code_hash : filebase64sha256("${path.module}/dummy.zip")
  
  # Ignore changes to source code during import process
  lifecycle {
    ignore_changes = [
      filename,
      source_code_hash
    ]
  }
  
  environment {
    variables = var.environment_variables
  }
  
  tags = var.tags
}

resource "aws_iam_role" "lambda_execution" {
  name = var.execution_role_name
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "bedrock_full_access" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days
  
  tags = var.tags
}