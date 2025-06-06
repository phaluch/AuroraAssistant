# Development Environment
# iac/environments/dev/main.tf

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Environment = "dev"
      Project     = "aurora"
      ManagedBy   = "terraform"
    }
  }
}

# AI Tooling Domain
module "ai_tooling" {
  source = "../../domains/ai_tooling"

  environment         = var.environment
  repo_root           = var.repo_root
  lambda_source_file  = var.lambda_source_file
  todoist_secret_name = var.todoist_secret_name
  lambda_layers       = var.lambda_layers
  bedrock_agent_arn   = "arn:aws:bedrock:${var.aws_region}:${var.aws_account_id}:agent/*"
}

# Agent Orchestration Domain
module "agent_orchestration" {
  source = "../../domains/agent_orchestration"
  
  project_name    = var.project_name
  environment = var.environment
  aws_region      = var.aws_region
  aws_account_id  = var.aws_account_id
  
  todoist_lambda_arn = module.ai_tooling.lambda_function_arn
  
  agent_instruction           = file("${path.module}/../../domains/agent_orchestration/agent_instruction.txt")
  todoist_api_schema         = file("${path.module}/../../domains/agent_orchestration/todoist_api_schema.yaml")
}

# User Interaction Domain
module "user_interaction" {
  source = "../../domains/user_interaction"
  
  project_name    = var.project_name
  environment = var.environment
  bedrock_agent_id       = module.agent_orchestration.bedrock_agent_id
  bedrock_agent_alias_id = module.agent_orchestration.bedrock_agent_alias_id
}