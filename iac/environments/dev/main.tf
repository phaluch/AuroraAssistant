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

# User Interaction Domain
module "user_interaction" {
  source = "../../domains/user_interaction"
  
  app_name    = var.app_name
  environment = var.environment
}