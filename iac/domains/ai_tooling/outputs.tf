output "lambda_function_arn" {
  description = "Todoist Lambda function ARN"
  value       = aws_lambda_function.todoist_tool.arn
}

output "lambda_function_name" {
  description = "Todoist Lambda function name"
  value       = aws_lambda_function.todoist_tool.function_name
}

output "lambda_role_arn" {
  description = "Todoist Lambda IAM role ARN"
  value       = aws_iam_role.todoist_lambda_role.arn
}