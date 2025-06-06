from typing import Dict, Any
from todoist_api_python.api import TodoistAPI
from todoist_utils import convert_to_dict

def handle_create_label(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle label creation."""
    print(f"[DEBUG] ---> Entering handle_create_label with params: {params}")
    name = params.get("name")
    if not name:
        print("[DEBUG] ERROR: Label name is missing.")
        raise ValueError("Label name is required for create operation")
    print(f"[DEBUG] Label name: '{name}'")
    
    print(f"[DEBUG] Calling api.add_label with name: '{name}'")
    label = api.add_label(name=name)
    print(f"[DEBUG] Received label object from API: {label}")

    label_dict = convert_to_dict(label)
    print(f"[DEBUG] Converted label object to dict: {label_dict}")

    response = {"message": f"Label '{label.name}' created successfully", **label_dict}
    print(f"[DEBUG] <--- Exiting handle_create_label with response: {response}")
    return response


def handle_update_label(api: TodoistAPI, label_id: str, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle label update."""
    print(f"[DEBUG] ---> Entering handle_update_label with label_id: {label_id}, params: {params}")

    update_params = {}
    if "name" in params:
        update_params["name"] = params["name"]
        print(f"[DEBUG] Added name to update_params: {update_params}")

    if not update_params:
        print("[DEBUG] ERROR: No update parameters provided.")
        raise ValueError("No update parameters provided")

    print(f"[DEBUG] Calling api.update_label for label_id '{label_id}' with params: {update_params}")
    label = api.update_label(label_id, **update_params)
    print(f"[DEBUG] Received updated label object from API: {label}")

    label_dict = convert_to_dict(label)
    print(f"[DEBUG] Converted updated label to dict: {label_dict}")

    response = {"message": "Label updated successfully", **label_dict}
    print(f"[DEBUG] <--- Exiting handle_update_label with response: {response}")
    return response


def handle_get_label(api: TodoistAPI, label_id: str) -> Dict[str, Any]:
    """Handle getting a single label."""
    print(f"[DEBUG] ---> Entering handle_get_label with label_id: {label_id}")

    print(f"[DEBUG] Calling api.get_label for label_id '{label_id}'")
    label = api.get_label(label_id)
    print(f"[DEBUG] Received label object from API: {label}")
    
    label_dict = convert_to_dict(label)
    print(f"[DEBUG] Converted label object to dict: {label_dict}")

    response = {"message": "Label retrieved successfully", **label_dict}
    print(f"[DEBUG] <--- Exiting handle_get_label with response: {response}")
    return response


def handle_list_labels(api: TodoistAPI) -> Dict[str, Any]:
    """Handle listing all labels."""
    print("[DEBUG] ---> Entering handle_list_labels")
    labels_data = []
    print("[DEBUG] Initialized empty labels_data list")

    print("[DEBUG] Calling api.get_labels() and iterating over all pages...")
    labels_iterator = api.get_labels()

    if isinstance(labels_iterator, list): # If the result is not an iterator but a simple list
        labels_iterator = [labels_iterator]

    for i, labels_page in enumerate(labels_iterator):
        print(f"[DEBUG] Processing page {i+1} of labels.")
        for j, label in enumerate(labels_page):
            print(f"[DEBUG]   Processing label {j+1} on page: {label.name}")
            label_dict = convert_to_dict(label)
            print(f"[DEBUG]   Converted label to dict: {label_dict}")
            labels_data.append(label_dict)

    print(f"[DEBUG] Finished processing all pages. Total labels retrieved: {len(labels_data)}")

    response = {
        "labels": labels_data,
        "count": len(labels_data),
        "message": f"Found {len(labels_data)} labels",
    }
    print(f"[DEBUG] <--- Exiting handle_list_labels with response: {response}")
    return response

def handle_delete_label(api: TodoistAPI, label_id: str) -> Dict[str, Any]:
    """Handle label deletion."""
    print(f"[DEBUG] ---> Entering handle_delete_label with label_id: {label_id}")

    print(f"[DEBUG] Calling api.delete_label for label_id '{label_id}'")
    result = api.delete_label(label_id)
    print(f"[DEBUG] API call result for delete_label: {result}")

    response = {
        "label_id": label_id,
        "message": "Label deleted successfully",
        "success": result,
    }
    print(f"[DEBUG] <--- Exiting handle_delete_label with response: {response}")
    return response