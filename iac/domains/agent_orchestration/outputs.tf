output "agent_id" {
  description = "Bedrock agent ID"
  value       = aws_bedrockagent_agent.todoist_assistant.agent_id
}

output "agent_arn" {
  description = "Bedrock agent ARN"
  value       = aws_bedrockagent_agent.todoist_assistant.agent_arn
}

output "agent_name" {
  description = "Bedrock agent name"
  value       = aws_bedrockagent_agent.todoist_assistant.agent_name
}

output "agent_role_arn" {
  description = "Bedrock agent IAM role ARN"
  value       = aws_iam_role.bedrock_agent_role.arn
}

output "action_group_id" {
  description = "Todoist action group ID"
  value       = aws_bedrockagent_agent_action_group.todoist_tool.action_group_id
}

output "bedrock_agent_id" {
  value = aws_bedrockagent_agent.todoist_assistant.agent_id
}

output "bedrock_agent_alias_id" {
  value = aws_bedrockagent_agent_alias.todoist_assistant.agent_alias_id
}