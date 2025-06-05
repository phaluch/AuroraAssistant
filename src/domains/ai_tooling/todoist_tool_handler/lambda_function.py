import json
import boto3
import os
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from todoist_api_python.api import TodoistAPI

# Initialize AWS clients
secrets_client = boto3.client("secretsmanager")

# Configuration
SECRET_NAME = os.environ.get("TODOIST_SECRET_NAME")


class TodoistJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects and removes null values."""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

    def encode(self, obj):
        # Remove null values recursively
        def remove_nulls(item):
            if isinstance(item, dict):
                return {k: remove_nulls(v) for k, v in item.items() if v is not None}
            elif isinstance(item, list):
                return [remove_nulls(v) for v in item if v is not None]
            else:
                return item

        cleaned_obj = remove_nulls(obj)
        return super().encode(cleaned_obj)


def get_api_token() -> str:
    """Retrieve Todoist API token from AWS Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        secret = json.loads(response["SecretString"])
        return secret.get("api_token", secret.get("token"))
    except Exception as e:
        raise Exception(f"Failed to retrieve API token: {str(e)}")


def parse_labels(labels_str: Optional[str]) -> Optional[List[str]]:
    """Parse comma-separated labels string into a list."""
    if not labels_str:
        return None
    return [label.strip() for label in labels_str.split(",") if label.strip()]


def convert_to_dict(obj) -> Dict[str, Any]:
    """Convert API response object to dictionary, handling nested objects."""
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    elif hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, list):
                result[key] = [
                    convert_to_dict(item) if hasattr(item, "__dict__") else item
                    for item in value
                ]
            elif hasattr(value, "__dict__"):
                result[key] = convert_to_dict(value)
            else:
                result[key] = value
        return result
    else:
        return obj


# Task handlers
def handle_create_task(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle task creation."""
    content = params.get("content")
    if not content:
        raise ValueError("Task content is required for create operation")

    task_params = {"content": content}

    # Add optional parameters
    if "description" in params:
        task_params["description"] = params["description"]
    if "project_id" in params:
        task_params["project_id"] = params["project_id"]
    if "priority" in params:
        try:
            priority = int(params["priority"])
            if 1 <= priority <= 4:
                task_params["priority"] = priority
        except ValueError:
            pass
    if "due_string" in params:
        task_params["due_string"] = params["due_string"]
    if "labels" in params:
        labels = parse_labels(params["labels"])
        if labels:
            task_params["labels"] = labels

    task = api.add_task(**task_params)
    task_dict = convert_to_dict(task)

    return {"message": f"Task '{task.content}' created successfully", **task_dict}


def handle_update_task(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle task update."""
    task_id = params.get("task_id")
    if not task_id:
        raise ValueError("Task ID is required for update operation")

    update_params = {}
    if "content" in params:
        update_params["content"] = params["content"]
    if "description" in params:
        update_params["description"] = params["description"]
    if "priority" in params:
        try:
            update_params["priority"] = int(params["priority"])
        except ValueError:
            pass
    if "due_string" in params:
        update_params["due_string"] = params["due_string"]

    if not update_params:
        raise ValueError("No update parameters provided")

    task = api.update_task(task_id, **update_params)
    task_dict = convert_to_dict(task)

    return {"message": "Task updated successfully", **task_dict}


def handle_complete_task(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle task completion."""
    task_id = params.get("task_id")
    if not task_id:
        raise ValueError("Task ID is required for complete operation")

    result = api.complete_task(task_id)

    return {
        "task_id": task_id,
        "message": "Task completed successfully",
        "success": result,
    }


def handle_get_task(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle getting a single task."""
    task_id = params.get("task_id")
    if not task_id:
        raise ValueError("Task ID is required for get operation")

    task = api.get_task(task_id)
    task_dict = convert_to_dict(task)

    return {"message": "Task retrieved successfully", **task_dict}


def handle_list_tasks(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle listing tasks with filters."""
    list_params = {}

    if "project_id" in params:
        list_params["project_id"] = params["project_id"]
    if "label" in params:
        list_params["label"] = params["label"]

    tasks_data = []

    # Use filter if provided
    if "filter" in params:
        tasks_iterator = api.filter_tasks(query=params["filter"])
    else:
        tasks_iterator = api.get_tasks(**list_params)

    # Get first page of results
    for tasks_page in tasks_iterator:
        for task in tasks_page:
            task_dict = convert_to_dict(task)
            tasks_data.append(task_dict)
        break  # Only get first page

    return {
        "tasks": tasks_data,
        "count": len(tasks_data),
        "message": f"Found {len(tasks_data)} tasks",
    }


# Project handlers
def handle_create_project(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle project creation."""
    name = params.get("name")
    if not name:
        raise ValueError("Project name is required for create operation")

    project_params = {"name": name}

    # Add optional parameters
    if "description" in params:
        project_params["description"] = params["description"]
    if "parent_id" in params:
        project_params["parent_id"] = params["parent_id"]

    project = api.add_project(**project_params)
    project_dict = convert_to_dict(project)

    return {"message": f"Project '{project.name}' created successfully", **project_dict}


def handle_update_project(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle project update."""
    project_id = params.get("project_id")
    if not project_id:
        raise ValueError("Project ID is required for update operation")

    update_params = {}
    if "name" in params:
        update_params["name"] = params["name"]
    if "description" in params:
        update_params["description"] = params["description"]

    if not update_params:
        raise ValueError("No update parameters provided")

    project = api.update_project(project_id, **update_params)
    project_dict = convert_to_dict(project)

    return {"message": "Project updated successfully", **project_dict}


def handle_get_project(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle getting a single project."""
    project_id = params.get("project_id")
    if not project_id:
        raise ValueError("Project ID is required for get operation")

    project = api.get_project(project_id)
    project_dict = convert_to_dict(project)

    return {"message": "Project retrieved successfully", **project_dict}


def handle_list_projects(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle listing projects."""
    projects_data = []

    # Get first page of results
    for projects_page in api.get_projects():
        for project in projects_page:
            project_dict = convert_to_dict(project)
            projects_data.append(project_dict)
        break  # Only get first page

    return {
        "projects": projects_data,
        "count": len(projects_data),
        "message": f"Found {len(projects_data)} projects",
    }


def handle_delete_project(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle project deletion."""
    project_id = params.get("project_id")
    if not project_id:
        raise ValueError("Project ID is required for delete operation")

    result = api.delete_project(project_id)

    return {
        "project_id": project_id,
        "message": "Project deleted successfully",
        "success": result,
    }


# Label handlers
def handle_create_label(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle label creation."""
    name = params.get("name")
    if not name:
        raise ValueError("Label name is required for create operation")

    label = api.add_label(name=name)
    label_dict = convert_to_dict(label)

    return {"message": f"Label '{label.name}' created successfully", **label_dict}


def handle_update_label(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle label update."""
    label_id = params.get("label_id")
    if not label_id:
        raise ValueError("Label ID is required for update operation")

    update_params = {}
    if "name" in params:
        update_params["name"] = params["name"]

    if not update_params:
        raise ValueError("No update parameters provided")

    label = api.update_label(label_id, **update_params)
    label_dict = convert_to_dict(label)

    return {"message": "Label updated successfully", **label_dict}


def handle_get_label(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle getting a single label."""
    label_id = params.get("label_id")
    if not label_id:
        raise ValueError("Label ID is required for get operation")

    label = api.get_label(label_id)
    label_dict = convert_to_dict(label)

    return {"message": "Label retrieved successfully", **label_dict}


def handle_list_labels(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle listing labels."""
    labels_data = []

    # Get first page of results
    for labels_page in api.get_labels():
        for label in labels_page:
            label_dict = convert_to_dict(label)
            labels_data.append(label_dict)
        break  # Only get first page

    return {
        "labels": labels_data,
        "count": len(labels_data),
        "message": f"Found {len(labels_data)} labels",
    }


def handle_delete_label(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle label deletion."""
    label_id = params.get("label_id")
    if not label_id:
        raise ValueError("Label ID is required for delete operation")

    result = api.delete_label(label_id)

    return {
        "label_id": label_id,
        "message": "Label deleted successfully",
        "success": result,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle Bedrock Agent requests for Todoist operations.

    Routes to appropriate handler based on apiPath and operation parameter.
    """
    try:
        # Parse Bedrock event
        action_group = event.get("actionGroup", "")
        api_path = event.get("apiPath", "")
        http_method = event.get("httpMethod", "POST")

        # Extract parameters
        parameters = {
            param["name"]: param["value"] for param in event.get("parameters", [])
        }

        # Debug logging
        print(f"API Path: {api_path}")
        print(f"Parameters: {parameters}")

        # Get operation type
        operation = parameters.get("operation")
        if not operation:
            raise ValueError("Operation parameter is required")

        # Get API token and initialize client
        api_token = get_api_token()

        # Route to appropriate handler based on apiPath and operation
        with TodoistAPI(api_token) as api:
            if api_path == "/tasks/manage":
                if operation == "create":
                    response_data = handle_create_task(api, parameters)
                elif operation == "update":
                    response_data = handle_update_task(api, parameters)
                elif operation == "complete":
                    response_data = handle_complete_task(api, parameters)
                elif operation == "get":
                    response_data = handle_get_task(api, parameters)
                elif operation == "list":
                    response_data = handle_list_tasks(api, parameters)
                else:
                    raise ValueError(f"Unsupported task operation: {operation}")

            elif api_path == "/projects/manage":
                if operation == "create":
                    response_data = handle_create_project(api, parameters)
                elif operation == "update":
                    response_data = handle_update_project(api, parameters)
                elif operation == "get":
                    response_data = handle_get_project(api, parameters)
                elif operation == "list":
                    response_data = handle_list_projects(api, parameters)
                elif operation == "delete":
                    response_data = handle_delete_project(api, parameters)
                else:
                    raise ValueError(f"Unsupported project operation: {operation}")

            elif api_path == "/labels/manage":
                if operation == "create":
                    response_data = handle_create_label(api, parameters)
                elif operation == "update":
                    response_data = handle_update_label(api, parameters)
                elif operation == "get":
                    response_data = handle_get_label(api, parameters)
                elif operation == "list":
                    response_data = handle_list_labels(api, parameters)
                elif operation == "delete":
                    response_data = handle_delete_label(api, parameters)
                else:
                    raise ValueError(f"Unsupported label operation: {operation}")

            else:
                raise ValueError(f"Unsupported API path: {api_path}")

        # Wrap response data
        final_response = {
            "success": True,
            "message": response_data.get(
                "message", f"Operation '{operation}' completed successfully"
            ),
            "data": response_data,
        }

        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "apiPath": api_path,
                "httpMethod": http_method,
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(final_response, cls=TodoistJSONEncoder)
                    }
                },
            },
        }

    except ValueError as e:
        # Handle validation errors
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "apiPath": event.get("apiPath", ""),
                "httpMethod": event.get("httpMethod", "POST"),
                "httpStatusCode": 400,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(
                            {
                                "success": False,
                                "error": "Bad Request",
                                "message": str(e),
                            },
                            cls=TodoistJSONEncoder,
                        )
                    }
                },
            },
        }

    except Exception as e:
        # Handle all other errors
        print(f"Error processing request: {str(e)}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "apiPath": event.get("apiPath", ""),
                "httpMethod": event.get("httpMethod", "POST"),
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(
                            {
                                "success": False,
                                "error": "Internal Server Error",
                                "message": "Operation failed",
                            },
                            cls=TodoistJSONEncoder,
                        )
                    }
                },
            },
        }
