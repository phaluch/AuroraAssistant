output "agent_id" {
  description = "Bedrock agent ID"
  value       = aws_bedrockagent_agent.main_agent.agent_id
}

output "agent_arn" {
  description = "Bedrock agent ARN"
  value       = aws_bedrockagent_agent.main_agent.agent_arn
}

output "agent_name" {
  description = "Bedrock agent name"
  value       = aws_bedrockagent_agent.main_agent.agent_name
}

output "agent_role_arn" {
  description = "Bedrock agent IAM role ARN"
  value       = aws_iam_role.bedrock_agent_role.arn
}

output "action_group_id" {
  description = "Todoist action group ID"
  value       = aws_bedrockagent_agent_action_group.todoist_tool.action_group_id
}