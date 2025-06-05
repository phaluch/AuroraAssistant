# User Interaction Domain Outputs
# iac/domains/user_interaction/outputs.tf

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.main_public_api.id
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.main_public_api.execution_arn
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.user_request_handler.lambda_function_arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.user_request_handler.lambda_function_name
}