import json
from typing import Dict, Any

from todoist_api_python.api import TodoistAPI

from todoist_utils import get_api_token, extract_path_parameter, TodoistJSONEncoder
from task_handlers import (
    handle_create_task,
    handle_update_task,
    handle_complete_task,
    handle_get_task,
    handle_list_tasks,
)
from project_handlers import (
    handle_create_project,
    handle_update_project,
    handle_get_project,
    handle_list_projects,
    handle_delete_project,
)
from label_handlers import (
    handle_create_label,
    handle_update_label,
    handle_get_label,
    handle_list_labels,
    handle_delete_label,
)
from snapshot_handler import handle_get_snapshot


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle Bedrock Agent requests for Todoist operations using REST conventions.
    """
    print("==================== LAMBDA INVOCATION START ====================")
    print(f"[DEBUG] Received event:\n{json.dumps(event, indent=2)}")
    print(f"[DEBUG] Received context: {context}")

    try:
        # Parse Bedrock event
        action_group = event.get("actionGroup", "")
        api_path = event.get("apiPath", "")
        http_method = event.get("httpMethod", "GET")
        print(f"[DEBUG] Parsed Event Details: actionGroup='{action_group}', apiPath='{api_path}', httpMethod='{http_method}'")

        # Extract parameters from both query parameters and request body
        parameters = {}

        # Extract query parameters
        if "parameters" in event:
            parameters.update({
                param["name"]: param["value"] for param in event.get("parameters", [])
            })

        # Extract request body parameters
        if "requestBody" in event and event["requestBody"]:
            content = event["requestBody"].get("content", {})
            for content_type, body_data in content.items():
                if "properties" in body_data:
                    parameters.update({
                        prop["name"]: prop["value"] for prop in body_data["properties"]
                    })

        print(f"[DEBUG] Extracted Parameters: {parameters}")

        # Get API token and initialize client
        print("[DEBUG] Getting API token...")
        api_token = get_api_token()
        print("[DEBUG] API token retrieved. Initializing TodoistAPI client.")

        response_data = None

        # Route to appropriate handler based on apiPath and HTTP method
        with TodoistAPI(api_token) as api:
            print("[DEBUG] TodoistAPI client context entered.")

            # DISCOVERY ENDPOINTS (Lists and Snapshot)
            if api_path == "/tasks" and http_method == "GET":
                print("[DEBUG] Routing to list tasks")
                response_data = handle_list_tasks(api, parameters)

            elif api_path == "/projects" and http_method == "GET":
                print("[DEBUG] Routing to list projects")
                response_data = handle_list_projects(api)

            elif api_path == "/labels" and http_method == "GET":
                print("[DEBUG] Routing to list labels")
                response_data = handle_list_labels(api)

            elif api_path == "/snapshot" and http_method == "GET":
                print("[DEBUG] Routing to get snapshot")
                response_data = handle_get_snapshot(api)

            # TASK OPERATIONS
            elif api_path == "/tasks" and http_method == "POST":
                print("[DEBUG] Routing to create task")
                response_data = handle_create_task(api, parameters)

            elif api_path.startswith("/tasks/") and http_method == "GET":
                print("[DEBUG] Routing to get specific task")
                task_id = extract_path_parameter(api_path, "tasks")
                if not task_id:
                    raise ValueError("Task ID is required for get operation")
                response_data = handle_get_task(api, task_id)

            elif api_path.startswith("/tasks/") and http_method == "PUT":
                print("[DEBUG] Routing to update task")
                task_id = extract_path_parameter(api_path, "tasks")
                if not task_id:
                    raise ValueError("Task ID is required for update operation")
                response_data = handle_update_task(api, task_id, parameters)

            elif api_path.endswith("/complete") and http_method == "POST":
                print("[DEBUG] Routing to complete task")
                task_id = extract_path_parameter(api_path, "tasks")
                if not task_id:
                    raise ValueError("Invalid path for task completion")
                response_data = handle_complete_task(api, task_id)

            # PROJECT OPERATIONS
            elif api_path == "/projects" and http_method == "POST":
                print("[DEBUG] Routing to create project")
                response_data = handle_create_project(api, parameters)

            elif api_path.startswith("/projects/") and http_method == "GET":
                print("[DEBUG] Routing to get specific project")
                project_id = extract_path_parameter(api_path, "projects")
                if not project_id:
                    raise ValueError("Project ID is required for get operation")
                response_data = handle_get_project(api, project_id)

            elif api_path.startswith("/projects/") and http_method == "PUT":
                print("[DEBUG] Routing to update project")
                project_id = extract_path_parameter(api_path, "projects")
                if not project_id:
                    raise ValueError("Project ID is required for update operation")
                response_data = handle_update_project(api, project_id, parameters)

            elif api_path.startswith("/projects/") and http_method == "DELETE":
                print("[DEBUG] Routing to delete project")
                project_id = extract_path_parameter(api_path, "projects")
                if not project_id:
                    raise ValueError("Project ID is required for delete operation")
                response_data = handle_delete_project(api, project_id)

            # LABEL OPERATIONS
            elif api_path == "/labels" and http_method == "POST":
                print("[DEBUG] Routing to create label")
                response_data = handle_create_label(api, parameters)

            elif api_path.startswith("/labels/") and http_method == "GET":
                print("[DEBUG] Routing to get specific label")
                label_id = extract_path_parameter(api_path, "labels")
                if not label_id:
                    raise ValueError("Label ID is required for get operation")
                response_data = handle_get_label(api, label_id)

            elif api_path.startswith("/labels/") and http_method == "PUT":
                print("[DEBUG] Routing to update label")
                label_id = extract_path_parameter(api_path, "labels")
                if not label_id:
                    raise ValueError("Label ID is required for update operation")
                response_data = handle_update_label(api, label_id, parameters)

            elif api_path.startswith("/labels/") and http_method == "DELETE":
                print("[DEBUG] Routing to delete label")
                label_id = extract_path_parameter(api_path, "labels")
                if not label_id:
                    raise ValueError("Label ID is required for delete operation")
                response_data = handle_delete_label(api, label_id)

            else:
                raise ValueError(f"Unsupported API path and method combination: {http_method} {api_path}")

        print(f"[DEBUG] Handler returned response_data: {response_data}")

        # Wrap response data
        final_response = {
            "success": True,
            "message": response_data.get("message", "Operation completed successfully"),
            "data": response_data,
        }
        print(f"[DEBUG] Constructed final_response object: {final_response}")

        lambda_return_value = {
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
        print(f"[DEBUG] Final Lambda return value (SUCCESS):\n{json.dumps(lambda_return_value, indent=2)}")
        print("==================== LAMBDA INVOCATION END ====================")
        return lambda_return_value

    except ValueError as e:
        print(f"[DEBUG] ERROR CAUGHT (ValueError): {str(e)}")
        # Handle validation errors
        error_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "apiPath": event.get("apiPath", ""),
                "httpMethod": event.get("httpMethod", "GET"),
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
        print(f"[DEBUG] Final Lambda return value (BAD REQUEST):\n{json.dumps(error_response, indent=2)}")
        print("==================== LAMBDA INVOCATION END (ERROR) ====================")
        return error_response

    except Exception as e:
        # Handle all other errors
        print(f"[DEBUG] ERROR CAUGHT (Exception): {str(e)}")
        error_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "apiPath": event.get("apiPath", ""),
                "httpMethod": event.get("httpMethod", "GET"),
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(
                            {
                                "success": False,
                                "error": "Internal Server Error",
                                "message": f"An unexpected error occurred: {str(e)}",
                            },
                            cls=TodoistJSONEncoder,
                        )
                    }
                },
            },
        }
        print(f"[DEBUG] Final Lambda return value (SERVER ERROR):\n{json.dumps(error_response, indent=2)}")
        print("==================== LAMBDA INVOCATION END (ERROR) ====================")
        return error_response