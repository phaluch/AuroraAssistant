# User Interaction Domain Variables
# iac/domains/user_interaction/variables.tf

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, stg, prd, qa)"
  type        = string
  
  validation {
    condition     = contains(["dev", "stg", "prd", "qa"], var.environment)
    error_message = "Environment must be one of: dev, stg, prd, qa."
  }
}

variable "bedrock_agent_id" {
  description = "Bedrock Agent ID"
  type        = string
}

variable "bedrock_agent_alias_id" {
  description = "Bedrock Agent Alias ID"  
  type        = string
}