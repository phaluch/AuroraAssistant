"""
Aurora Assistant - User Request Handler Lambda
Handles API Gateway requests to invoke Bedrock Agent
"""

import json
import os
import uuid
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
import logging

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID')

# Initialize Bedrock client (outside handler for connection reuse)
bedrock_agent = boto3.client('bedrock-agent-runtime')


class BedrockAgentError(Exception):
    """Custom exception for Bedrock Agent related errors"""
    pass


def _validate_request_body(body: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate required parameters in request body
    
    Args:
        body: Parsed request body
        
    Returns:
        Dict containing validation errors
        
    Raises:
        None - returns errors dict instead
    """
    errors = {}
    
    if not body.get('inputText'):
        errors['inputText'] = 'inputText is required'
        
    # Allow override of environment defaults
    agent_id = body.get('agentId', AGENT_ID)
    if not agent_id:
        errors['agentId'] = 'agentId must be provided in request or BEDROCK_AGENT_ID environment variable'
        
    return errors


def _build_invoke_params(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build parameters for bedrock agent invocation
    
    Args:
        body: Validated request body
        
    Returns:
        Dict of parameters for invoke_agent call
    """
    # Use provided values or environment defaults
    agent_id = body.get('agentId', AGENT_ID)
    agent_alias_id = body.get('agentAliasId', AGENT_ALIAS_ID)
    session_id = body.get('sessionId', str(uuid.uuid4()))
    
    invoke_params = {
        'agentId': agent_id,
        'agentAliasId': agent_alias_id,
        'sessionId': session_id,
        'inputText': body['inputText']
    }
    
    # Optional parameters
    optional_params = [
        'enableTrace', 'endSession', 'memoryId', 'sessionState',
        'bedrockModelConfigurations', 'sourceArn', 'streamingConfigurations'
    ]
    
    for param in optional_params:
        if param in body:
            invoke_params[param] = body[param]
            
    return invoke_params


def _process_agent_response(response: Dict[str, Any], enable_trace: bool = False) -> Dict[str, Any]:
    """
    Process streaming response from Bedrock Agent
    
    Args:
        response: Response from invoke_agent call
        enable_trace: Whether to include trace information
        
    Returns:
        Processed response dict
        
    Raises:
        BedrockAgentError: If response processing fails
    """
    completion = ""
    citations = []
    traces = []
    
    try:
        for event in response.get('completion', []):
            if 'chunk' in event:
                chunk = event['chunk']
                
                # Extract text content
                if 'bytes' in chunk:
                    completion += chunk['bytes'].decode('utf-8')
                    
                # Extract citations
                if 'attribution' in chunk and 'citations' in chunk['attribution']:
                    citations.extend(chunk['attribution']['citations'])
                    
            elif 'trace' in event and enable_trace:
                traces.append(event['trace'])
                
            elif 'returnControl' in event:
                # Handle function calling scenario
                return {
                    'type': 'returnControl',
                    'returnControl': event['returnControl']
                }
                
    except Exception as e:
        logger.error(f"Error processing agent response: {str(e)}")
        raise BedrockAgentError(f"Failed to process agent response: {str(e)}")
    
    result = {
        'completion': completion,
        'citations': citations
    }
    
    if enable_trace:
        result['traces'] = traces
        
    return result


def _create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create standardized API Gateway response
    
    Args:
        status_code: HTTP status code
        body: Response body dict
        
    Returns:
        API Gateway response format
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Configure as needed
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body, default=str)  # Handle datetime serialization
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for Aurora Assistant user requests
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    # Structured logging with context
    request_id = context.aws_request_id if context else str(uuid.uuid4())
    logger.info(
        "Processing user request",
        extra={
            'request_id': request_id,
            'domain': 'user-interaction',
            'component': 'user-request-handler'
        }
    )
    
    try:
        # Parse request body
        if not event.get('body'):
            logger.warning("Missing request body", extra={'request_id': request_id})
            return _create_response(400, {'error': 'Missing request body'})
            
        try:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}", extra={'request_id': request_id})
            return _create_response(400, {'error': 'Invalid JSON in request body'})
        
        # Validate request
        validation_errors = _validate_request_body(body)
        if validation_errors:
            logger.warning("Request validation failed", extra={
                'request_id': request_id,
                'errors': validation_errors
            })
            return _create_response(400, {'error': 'Validation failed', 'details': validation_errors})
        
        # Build invocation parameters
        invoke_params = _build_invoke_params(body)
        session_id = invoke_params['sessionId']
        
        logger.info("Invoking Bedrock Agent", extra={
            'request_id': request_id,
            'session_id': session_id,
            'agent_id': invoke_params['agentId']
        })
        
        # Invoke Bedrock Agent
        try:
            response = bedrock_agent.invoke_agent(**invoke_params)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            logger.error("Bedrock Agent invocation failed", extra={
                'request_id': request_id,
                'error_code': error_code,
                'error_message': error_message
            })
            
            return _create_response(502, {
                'error': 'Agent invocation failed',
                'details': f"{error_code}: {error_message}"
            })
        
        # Process response
        enable_trace = body.get('enableTrace', False)
        result = _process_agent_response(response, enable_trace)
        
        # Add session ID to result
        result['sessionId'] = session_id
        
        logger.info("Request processed successfully", extra={
            'request_id': request_id,
            'session_id': session_id,
            'completion_length': len(result.get('completion', '')),
            'citations_count': len(result.get('citations', []))
        })
        
        return _create_response(200, result)
        
    except BedrockAgentError as e:
        logger.error(f"Bedrock Agent error: {str(e)}", extra={'request_id': request_id})
        return _create_response(502, {'error': str(e)})
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra={'request_id': request_id})
        return _create_response(500, {'error': 'Internal server error'})