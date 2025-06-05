# Lambda Function Module Variables
# iac/modules/aws_lambda_function/variables.tf

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "execution_role_name" {
  description = "Name of the IAM role for Lambda execution"
  type        = string
}

variable "handler" {
  description = "Lambda function handler"
  type        = string
  default     = "lambda_function.lambda_handler"
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.12"
}

variable "timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 60
}

variable "memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 128
}

variable "filename" {
  description = "Path to the Lambda deployment package"
  type        = string
  default     = null
}

variable "source_code_hash" {
  description = "Hash of the Lambda source code"
  type        = string
  default     = null
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function"
  type        = map(string)
  default     = {}
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}