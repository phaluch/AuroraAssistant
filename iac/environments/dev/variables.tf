# Development Environment Variables
# iac/environments/dev/variables.tf

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "aurora"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "aurora-cli"
}

variable "bedrock_agent_id" {
  description = "Bedrock Agent ID"
  type        = string
}

variable "bedrock_agent_alias_id" {
  description = "Bedrock Agent Alias ID"
  type        = string
}
