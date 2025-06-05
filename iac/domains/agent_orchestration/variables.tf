variable "environment" {
  description = "Environment name (dev, stg, prd)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "todoist_lambda_arn" {
  description = "ARN of the Todoist Lambda function"
  type        = string
}

variable "agent_instruction" {
  description = "Instructions for the Bedrock agent"
  type        = string
}

variable "todoist_api_schema" {
  description = "OpenAPI schema for Todoist action group"
  type        = string
}
