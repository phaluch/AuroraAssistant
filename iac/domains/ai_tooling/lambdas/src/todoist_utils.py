import json
import boto3
import os
from datetime import datetime, date
from typing import Dict, Any, List, Optional

# Initialize AWS clients
print("[DEBUG] Initializing boto3 client for Secrets Manager")
secrets_client = boto3.client("secretsmanager")
print("[DEBUG] Secrets Manager client initialized")

# Configuration
print("[DEBUG] Reading environment variable for SECRET_NAME")
SECRET_NAME = os.environ.get("TODOIST_SECRET_NAME")
print(f"[DEBUG] SECRET_NAME is set to: {SECRET_NAME}")


class TodoistJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects and removes null values."""

    def default(self, obj):
        print(f"[DEBUG] TodoistJSONEncoder.default called for object of type: {type(obj)}")
        if isinstance(obj, (datetime, date)):
            iso_format = obj.isoformat()
            print(f"[DEBUG]   Encoding datetime object to ISO format: {iso_format}")
            return iso_format
        print("[DEBUG]   Falling back to super().default")
        return super().default(obj)

    def encode(self, obj):
        print(f"[DEBUG] TodoistJSONEncoder.encode called for object: {obj}")

        # Remove null values recursively
        def remove_nulls(item):
            print(f"[DEBUG]   remove_nulls called for item: {item}")
            if isinstance(item, dict):
                print("[DEBUG]     Item is a dict, removing nulls from values.")
                return {k: remove_nulls(v) for k, v in item.items() if v is not None}
            elif isinstance(item, list):
                print("[DEBUG]     Item is a list, removing nulls from elements.")
                return [remove_nulls(v) for v in item if v is not None]
            else:
                print("[DEBUG]     Item is not a dict or list, returning as is.")
                return item

        print("[DEBUG] Cleaning object to remove null values.")
        cleaned_obj = remove_nulls(obj)
        print(f"[DEBUG] Object after cleaning null values: {cleaned_obj}")
        print("[DEBUG] Calling super().encode on the cleaned object.")
        return super().encode(cleaned_obj)


def get_api_token() -> str:
    """Retrieve Todoist API token from AWS Secrets Manager."""
    print("[DEBUG] ---> Entering get_api_token function")
    print(f"[DEBUG] Attempting to retrieve secret with SecretId: {SECRET_NAME}")
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        print("[DEBUG] Successfully called get_secret_value")
        print(f"[DEBUG] Raw response from Secrets Manager: {response}")
        secret = json.loads(response["SecretString"])
        print(f"[DEBUG] Parsed secret string: {secret}")
        token = secret.get("api_token", secret.get("token"))
        print(f"[DEBUG] Extracted token: {'*'*len(token) if token else 'None'}")
        print("[DEBUG] <--- Exiting get_api_token function successfully")
        return token
    except Exception as e:
        print(f"[DEBUG] ERROR: Failed to retrieve API token: {str(e)}")
        raise Exception(f"Failed to retrieve API token: {str(e)}")


def parse_labels(labels_str: Optional[str]) -> Optional[List[str]]:
    """Parse comma-separated labels string into a list."""
    print(f"[DEBUG] ---> Entering parse_labels with string: '{labels_str}'")
    if not labels_str:
        print("[DEBUG] Input string is empty or None. Returning None.")
        print("[DEBUG] <--- Exiting parse_labels")
        return None
    
    labels_list = [label.strip() for label in labels_str.split(",") if label.strip()]
    print(f"[DEBUG] Parsed list of labels: {labels_list}")
    print("[DEBUG] <--- Exiting parse_labels")
    return labels_list


def convert_to_dict(obj) -> Dict[str, Any]:
    """Convert API response object to dictionary, handling nested objects."""
    print(f"[DEBUG] ---> Entering convert_to_dict for object of type: {type(obj)}")
    if hasattr(obj, "to_dict"):
        print("[DEBUG]   Object has 'to_dict' method. Calling it.")
        result = obj.to_dict()
        print(f"[DEBUG]   Result from to_dict(): {result}")
        print("[DEBUG] <--- Exiting convert_to_dict")
        return result
    elif hasattr(obj, "__dict__"):
        print("[DEBUG]   Object has '__dict__' attribute. Converting manually.")
        result = {}
        for key, value in obj.__dict__.items():
            print(f"[DEBUG]     Processing key: '{key}' with value: {value}")
            if isinstance(value, list):
                print(f"[DEBUG]       Value for '{key}' is a list. Converting its items.")
                result[key] = [
                    convert_to_dict(item) if hasattr(item, "__dict__") else item
                    for item in value
                ]
            elif hasattr(value, "__dict__"):
                print(f"[DEBUG]       Value for '{key}' is a nested object. Converting it recursively.")
                result[key] = convert_to_dict(value)
            else:
                print(f"[DEBUG]       Value for '{key}' is a primitive. Assigning directly.")
                result[key] = value
        print(f"[DEBUG]   Manual conversion result: {result}")
        print("[DEBUG] <--- Exiting convert_to_dict")
        return result
    else:
        print("[DEBUG]   Object is not convertible. Returning as is.")
        print(f"[DEBUG] <--- Exiting convert_to_dict")
        return obj


def extract_path_parameter(api_path: str, resource_name: str) -> Optional[str]:
    """
    Extracts an ID from a RESTful API path.
    e.g., extract_path_parameter("/tasks/12345/complete", "tasks") -> "12345"
    """
    print(f"[DEBUG] Extracting ID for '{resource_name}' from path: {api_path}")
    parts = api_path.strip("/").split("/")
    # Expected path format: /<resource_name>/<id>/...
    if len(parts) >= 2 and parts[0] == resource_name:
        param_value = parts[1]
        print(f"[DEBUG] Found ID: {param_value}")
        return param_value
    print(f"[DEBUG] No ID found for '{resource_name}' in path")
    return None