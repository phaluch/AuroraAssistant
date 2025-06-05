# User Interaction Domain
# iac/domains/user_interaction/main.tf

locals {
  common_tags = {
    Name   = ""  # Will be set per resource
    domain = "user-interaction"
  }
}

# Build Lambda deployment package
data "archive_file" "user_request_handler" {
  type        = "zip"
  source_dir  = "${path.root}/../../src/domains/user_interaction/api_handlers/user_request_handler"
  output_path = "${path.module}/user_request_handler.zip"
}

# Lambda Function for handling user requests
module "user_request_handler" {
  source = "../../modules/aws_lambda_function"
  
  function_name       = "aurora-dev-ui-lambda-user-request-handler"
  execution_role_name = "aurora-dev-ui-iam-user-request-handler-exec-role"
  handler            = "app.lambda_handler"
  runtime            = "python3.12"
  timeout            = 60
  memory_size        = 128
  
  # Deployment package
  filename         = data.archive_file.user_request_handler.output_path
  source_code_hash = data.archive_file.user_request_handler.output_base64sha256

  environment_variables = {
    BEDROCK_AGENT_ID       = var.bedrock_agent_id
    BEDROCK_AGENT_ALIAS_ID = var.bedrock_agent_alias_id
    AWS_REGION            = var.aws_region
  }

  tags = merge(local.common_tags, {
    Name = "aurora-dev-ui-lambda-user-request-handler"
  })
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "main_public_api" {
  name        = "${var.app_name}-${var.environment}-ui-agw-main-public-api"
  description = "Main public API for Aurora Assistant"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${var.app_name}-${var.environment}-ui-agw-main-public-api"
  })
}

# API Gateway Resource for /invoke-agent
resource "aws_api_gateway_resource" "invoke_agent" {
  rest_api_id = aws_api_gateway_rest_api.main_public_api.id
  parent_id   = aws_api_gateway_rest_api.main_public_api.root_resource_id
  path_part   = "invoke-agent"
}

# API Gateway Method (POST)
resource "aws_api_gateway_method" "invoke_agent_post" {
  rest_api_id   = aws_api_gateway_rest_api.main_public_api.id
  resource_id   = aws_api_gateway_resource.invoke_agent.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Method (OPTIONS for CORS)
resource "aws_api_gateway_method" "invoke_agent_options" {
  rest_api_id   = aws_api_gateway_rest_api.main_public_api.id
  resource_id   = aws_api_gateway_resource.invoke_agent.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# API Gateway Integration (POST)
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.main_public_api.id
  resource_id = aws_api_gateway_resource.invoke_agent.id
  http_method = aws_api_gateway_method.invoke_agent_post.http_method
  
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = module.user_request_handler.lambda_function_invoke_arn
}

# API Gateway Integration Response (POST)
resource "aws_api_gateway_method_response" "lambda_response_200" {
  rest_api_id = aws_api_gateway_rest_api.main_public_api.id
  resource_id = aws_api_gateway_resource.invoke_agent.id
  http_method = aws_api_gateway_method.invoke_agent_post.http_method
  status_code = "200"
  
  response_models = {
    "application/json" = "Empty"
  }
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.user_request_handler.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  
  source_arn = "${aws_api_gateway_rest_api.main_public_api.execution_arn}/*/*"
}