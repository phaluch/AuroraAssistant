import json
import boto3
import uuid
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to invoke Bedrock Agent via API Gateway
    """
    print("Event: ", event)
    print("Context: ", context)
    try:
        # Initialize Bedrock Agent Runtime client
        bedrock_agent = boto3.client("bedrock-agent-runtime")

        # Parse request body
        if "body" in event:
            if isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event["body"]
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing request body"}),
            }

        # Extract required parameters
        agent_id = body.get("agentId")
        agent_alias_id = body.get("agentAliasId")
        input_text = body.get("inputText")

        if not all([agent_id, agent_alias_id, input_text]):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "error": "Missing required parameters: agentId, agentAliasId, inputText"
                    }
                ),
            }

        # Generate session ID if not provided
        session_id = body.get("sessionId", str(uuid.uuid4()))

        # Build invoke_agent parameters
        invoke_params = {
            "agentId": agent_id,
            "agentAliasId": "36LYLPM6MA",
            "sessionId": session_id,
            "inputText": input_text,
            "sessionId": "androidv1Session",
            "memoryId": "androidv1Memory",
        }

        # Add optional parameters if provided
        if "enableTrace" in body:
            invoke_params["enableTrace"] = body["enableTrace"]

        if "endSession" in body:
            invoke_params["endSession"] = body["endSession"]

        if "memoryId" in body:
            invoke_params["memoryId"] = body["memoryId"]

        if "sessionState" in body:
            invoke_params["sessionState"] = body["sessionState"]

        if "bedrockModelConfigurations" in body:
            invoke_params["bedrockModelConfigurations"] = body[
                "bedrockModelConfigurations"
            ]

        if "sourceArn" in body:
            invoke_params["sourceArn"] = body["sourceArn"]

        if "streamingConfigurations" in body:
            invoke_params["streamingConfigurations"] = body["streamingConfigurations"]

        # Invoke the agent
        response = bedrock_agent.invoke_agent(**invoke_params)

        # Process the streaming response
        completion = ""
        citations = []
        traces = []

        for event in response["completion"]:
            if "chunk" in event:
                chunk = event["chunk"]
                if "bytes" in chunk:
                    completion += chunk["bytes"].decode("utf-8")
                if "attribution" in chunk and "citations" in chunk["attribution"]:
                    citations.extend(chunk["attribution"]["citations"])

            elif "trace" in event:
                traces.append(event["trace"])

            elif "returnControl" in event:
                # Handle return control scenario
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(
                        {
                            "type": "returnControl",
                            "sessionId": session_id,
                            "returnControl": event["returnControl"],
                        }
                    ),
                }

        # Return successful response
        result = {
            "sessionId": session_id,
            "completion": completion,
            "citations": citations,
        }

        # Include traces if enableTrace was true
        if body.get("enableTrace", False):
            result["traces"] = traces

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
