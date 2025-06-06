from typing import Dict, Any
from todoist_api_python.api import TodoistAPI
from todoist_utils import convert_to_dict


def handle_create_project(api: TodoistAPI, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle project creation."""
    print(f"[DEBUG] ---> Entering handle_create_project with params: {params}")
    name = params.get("name")
    if not name:
        print("[DEBUG] ERROR: Project name is missing.")
        raise ValueError("Project name is required for create operation")
    print(f"[DEBUG] Project name: '{name}'")
    
    project_params = {"name": name}
    print(f"[DEBUG] Initial project_params: {project_params}")

    # Add optional parameters
    if "description" in params:
        project_params["description"] = params["description"]
        print(f"[DEBUG] Added description to project_params: {project_params}")
    if "parent_id" in params:
        project_params["parent_id"] = params["parent_id"]
        print(f"[DEBUG] Added parent_id to project_params: {project_params}")

    print(f"[DEBUG] Calling api.add_project with params: {project_params}")
    project = api.add_project(**project_params)
    print(f"[DEBUG] Received project object from API: {project}")

    project_dict = convert_to_dict(project)
    print(f"[DEBUG] Converted project object to dict: {project_dict}")

    response = {"message": f"Project '{project.name}' created successfully", **project_dict}
    print(f"[DEBUG] <--- Exiting handle_create_project with response: {response}")
    return response


def handle_update_project(api: TodoistAPI, project_id: str, params: Dict[str, str]) -> Dict[str, Any]:
    """Handle project update."""
    print(f"[DEBUG] ---> Entering handle_update_project with project_id: {project_id}, params: {params}")

    update_params = {}
    print(f"[DEBUG] Initial update_params: {update_params}")
    if "name" in params:
        update_params["name"] = params["name"]
        print(f"[DEBUG] Added name to update_params: {update_params}")
    if "description" in params:
        update_params["description"] = params["description"]
        print(f"[DEBUG] Added description to update_params: {update_params}")

    if not update_params:
        print("[DEBUG] ERROR: No update parameters provided.")
        raise ValueError("No update parameters provided")

    print(f"[DEBUG] Calling api.update_project for project_id '{project_id}' with params: {update_params}")
    project = api.update_project(project_id, **update_params)
    print(f"[DEBUG] Received updated project object from API: {project}")

    project_dict = convert_to_dict(project)
    print(f"[DEBUG] Converted updated project to dict: {project_dict}")

    response = {"message": "Project updated successfully", **project_dict}
    print(f"[DEBUG] <--- Exiting handle_update_project with response: {response}")
    return response


def handle_get_project(api: TodoistAPI, project_id: str) -> Dict[str, Any]:
    """Handle getting a single project."""
    print(f"[DEBUG] ---> Entering handle_get_project with project_id: {project_id}")

    print(f"[DEBUG] Calling api.get_project for project_id '{project_id}'")
    project = api.get_project(project_id)
    print(f"[DEBUG] Received project object from API: {project}")

    project_dict = convert_to_dict(project)
    print(f"[DEBUG] Converted project object to dict: {project_dict}")

    response = {"message": "Project retrieved successfully", **project_dict}
    print(f"[DEBUG] <--- Exiting handle_get_project with response: {response}")
    return response


def handle_list_projects(api: TodoistAPI) -> Dict[str, Any]:
    """Handle listing all projects."""
    print("[DEBUG] ---> Entering handle_list_projects")
    projects_data = []
    print("[DEBUG] Initialized empty projects_data list")

    print("[DEBUG] Calling api.get_projects() and iterating over all pages...")
    projects_iterator = api.get_projects()

    if isinstance(projects_iterator, list): # If the result is not an iterator but a simple list
        projects_iterator = [projects_iterator]

    for i, projects_page in enumerate(projects_iterator):
        print(f"[DEBUG] Processing page {i+1} of projects.")
        for j, project in enumerate(projects_page):
            print(f"[DEBUG]   Processing project {j+1} on page: {project.name}")
            project_dict = convert_to_dict(project)
            print(f"[DEBUG]   Converted project to dict: {project_dict}")
            projects_data.append(project_dict)
    
    print(f"[DEBUG] Finished processing all pages. Total projects retrieved: {len(projects_data)}")

    response = {
        "projects": projects_data,
        "count": len(projects_data),
        "message": f"Found {len(projects_data)} projects",
    }
    print(f"[DEBUG] <--- Exiting handle_list_projects with response: {response}")
    return response


def handle_delete_project(api: TodoistAPI, project_id: str) -> Dict[str, Any]:
    """Handle project deletion."""
    print(f"[DEBUG] ---> Entering handle_delete_project with project_id: {project_id}")

    print(f"[DEBUG] Calling api.delete_project for project_id '{project_id}'")
    result = api.delete_project(project_id)
    print(f"[DEBUG] API call result for delete_project: {result}")

    response = {
        "project_id": project_id,
        "message": "Project deleted successfully",
        "success": result,
    }
    print(f"[DEBUG] <--- Exiting handle_delete_project with response: {response}")
    return response