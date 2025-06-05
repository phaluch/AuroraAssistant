variable "environment" {
  description = "Environment name (dev, stg, prd)"
  type        = string
}

variable "lambda_source_file" {
  description = "Path to Lambda Python source file"
  type        = string
}

variable "todoist_secret_name" {
  description = "Name of Secrets Manager secret containing Todoist API token"
  type        = string
}

variable "lambda_layers" {
  description = "List of Lambda layer ARNs"
  type        = list(string)
  default     = []
}

variable "bedrock_agent_arn" {
  description = "ARN of the Bedrock agent (for Lambda permissions)"
  type        = string
}