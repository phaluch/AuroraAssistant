from typing import Dict, Any
from todoist_api_python.api import TodoistAPI
from todoist_utils import parse_labels, convert_to_dict


def handle_create_task(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle task creation."""
    print(f"[DEBUG] ---> Entering handle_create_task with params: {params}")
    content = params.get("content")
    if not content:
        print("[DEBUG] ERROR: Task content is missing.")
        raise ValueError("Task content is required for create operation")
    print(f"[DEBUG] Task content: '{content}'")

    task_params = {"content": content}
    print(f"[DEBUG] Initial task_params: {task_params}")

    # Add optional parameters
    if "description" in params:
        task_params["description"] = params["description"]
        print(f"[DEBUG] Added description to params: {task_params}")
    if "project_id" in params:
        task_params["project_id"] = params["project_id"]
        print(f"[DEBUG] Added project_id to params: {task_params}")
    if "priority" in params:
        try:
            priority = int(params["priority"])
            if 1 <= priority <= 4:
                task_params["priority"] = priority
                print(f"[DEBUG] Added valid priority to params: {task_params}")
        except ValueError:
            print(f"[DEBUG] Invalid priority value, skipping: {params['priority']}")
            pass
    if "due_string" in params:
        task_params["due_string"] = params["due_string"]
        print(f"[DEBUG] Added due_string to params: {task_params}")
    if "labels" in params:
        labels = parse_labels(params["labels"])
        if labels:
            task_params["labels"] = labels
            print(f"[DEBUG] Added labels to params: {task_params}")

    print(f"[DEBUG] Calling api.add_task with params: {task_params}")
    task = api.add_task(**task_params)
    print(f"[DEBUG] Received task object from API: {task}")
    
    task_dict = convert_to_dict(task)
    print(f"[DEBUG] Converted task object to dict: {task_dict}")

    response = {"message": f"Task '{task.content}' created successfully", **task_dict}
    print(f"[DEBUG] <--- Exiting handle_create_task with response: {response}")
    return response


def handle_update_task(api: TodoistAPI, task_id: str, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle task update."""
    print(f"[DEBUG] ---> Entering handle_update_task with task_id: {task_id}, params: {params}")

    update_params = {}
    print("[DEBUG] Initial update_params: {}")
    if "content" in params:
        update_params["content"] = params["content"]
        print(f"[DEBUG] Added content to update_params: {update_params}")
    if "description" in params:
        update_params["description"] = params["description"]
        print(f"[DEBUG] Added description to update_params: {update_params}")
    if "priority" in params:
        try:
            update_params["priority"] = int(params["priority"])
            print(f"[DEBUG] Added priority to update_params: {update_params}")
        except ValueError:
            print(f"[DEBUG] Invalid priority value, skipping: {params['priority']}")
            pass
    if "due_string" in params:
        update_params["due_string"] = params["due_string"]
        print(f"[DEBUG] Added due_string to update_params: {update_params}")
    if "labels" in params:
        labels = parse_labels(params["labels"])
        if labels:
            update_params["labels"] = labels
            print(f"[DEBUG] Added labels to update_params: {update_params}")

    if not update_params:
        print("[DEBUG] ERROR: No update parameters were provided.")
        raise ValueError("No update parameters provided")

    print(f"[DEBUG] Calling api.update_task for task_id '{task_id}' with params: {update_params}")
    task = api.update_task(task_id, **update_params)
    print(f"[DEBUG] Received updated task object from API: {task}")

    task_dict = convert_to_dict(task)
    print(f"[DEBUG] Converted updated task to dict: {task_dict}")

    response = {"message": "Task updated successfully", **task_dict}
    print(f"[DEBUG] <--- Exiting handle_update_task with response: {response}")
    return response


def handle_complete_task(api: TodoistAPI, task_id: str) -> Dict[str, Any]:
    """Handle task completion."""
    print(f"[DEBUG] ---> Entering handle_complete_task with task_id: {task_id}")

    print(f"[DEBUG] Calling api.complete_task for task_id '{task_id}'")
    result = api.complete_task(task_id)
    print(f"[DEBUG] API call result for complete_task: {result}")

    response = {
        "task_id": task_id,
        "message": "Task completed successfully",
        "success": result,
    }
    print(f"[DEBUG] <--- Exiting handle_complete_task with response: {response}")
    return response


def handle_get_task(api: TodoistAPI, task_id: str) -> Dict[str, Any]:
    """Handle getting a single task."""
    print(f"[DEBUG] ---> Entering handle_get_task with task_id: {task_id}")
    
    print(f"[DEBUG] Calling api.get_task for task_id '{task_id}'")
    task = api.get_task(task_id)
    print(f"[DEBUG] Received task object from API: {task}")
    
    task_dict = convert_to_dict(task)
    print(f"[DEBUG] Converted task object to dict: {task_dict}")

    response = {"message": "Task retrieved successfully", **task_dict}
    print(f"[DEBUG] <--- Exiting handle_get_task with response: {response}")
    return response


def handle_list_tasks(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle listing tasks with filters, with full pagination."""
    print(f"[DEBUG] ---> Entering handle_list_tasks with params: {params}")
    list_params = {}
    print(f"[DEBUG] Initial list_params: {list_params}")

    if "project_id" in params:
        list_params["project_id"] = params["project_id"]
        print(f"[DEBUG] Added project_id to list_params: {list_params}")
    if "label" in params:
        list_params["label"] = params["label"]
        print(f"[DEBUG] Added label to list_params: {list_params}")

    tasks_data = []
    print("[DEBUG] Initialized empty tasks_data list")

    # Use filter if provided
    if "filter" in params:
        print(f"[DEBUG] Using filter to get tasks. Filter: '{params['filter']}'")
        # Note: filter_tasks is not a standard method in the library. Assuming it's a custom extension or should be get_tasks.
        # The original code had `api.filter_tasks` which does not exist in the official todoist-api-python
        # Assuming the intent was to use the `filter` parameter of `get_tasks`
        list_params['filter'] = params['filter']
        tasks_iterator = api.get_tasks(**list_params)

    else:
        print(f"[DEBUG] Using get_tasks to list tasks with params: {list_params}")
        tasks_iterator = api.get_tasks(**list_params)
    
    if isinstance(tasks_iterator, list): # If the result is not an iterator but a simple list
        tasks_iterator = [tasks_iterator]

    print("[DEBUG] Iterating over all pages of results...")
    for i, tasks_page in enumerate(tasks_iterator):
        print(f"[DEBUG] Processing page {i+1} of tasks.")
        for j, task in enumerate(tasks_page):
            print(f"[DEBUG]   Processing task {j+1} on page: {task.content}")
            task_dict = convert_to_dict(task)
            print(f"[DEBUG]   Converted task to dict: {task_dict}")
            tasks_data.append(task_dict)
    
    print(f"[DEBUG] Finished processing all pages. Total tasks retrieved: {len(tasks_data)}")

    response = {
        "tasks": tasks_data,
        "count": len(tasks_data),
        "message": f"Found {len(tasks_data)} tasks",
    }
    print(f"[DEBUG] <--- Exiting handle_list_tasks with response: {response}")
    return response