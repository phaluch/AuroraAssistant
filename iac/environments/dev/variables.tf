# Development Environment Variables
# iac/environments/dev/variables.tf

variable "project_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "lambda_source_file" {
  description = "Path to Lambda Python script"
  type        = string
}

variable "todoist_secret_name" {
  description = "Name of Secrets Manager secret containing Todoist API token"
  type        = string
}

variable "lambda_layers" {
  description = "List of Lambda layer ARNs"
  type        = list(string)
}

variable "repo_root" {
  type        = string
  description = "Path to the root of the repo for relative file access"
}
