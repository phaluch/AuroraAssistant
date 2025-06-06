from typing import Dict, Any
from todoist_api_python.api import TodoistAPI

def handle_get_snapshot(api: TodoistAPI) -> Dict[str, Any]:
    """Handle retrieving a snapshot of all projects and their tasks/labels."""
    print("[DEBUG] ---> Entering handle_get_snapshot")
    print("[DEBUG] Starting snapshot retrieval...")
    
    # Correctly flatten paginated API responses into single lists
    try:
        print("[DEBUG] Attempting to get all projects with pagination flattening...")
        all_projects = [project for page in api.get_projects() for project in page]
        print(f"[DEBUG] Successfully retrieved {len(all_projects)} projects via pagination")
        
        print("[DEBUG] Attempting to get all labels with pagination flattening...")
        all_labels_list = [label for page in api.get_labels() for label in page]
        print(f"[DEBUG] Successfully retrieved {len(all_labels_list)} labels via pagination")
    except TypeError as e:
        print(f"[DEBUG] WARNING: Pagination failed with TypeError: {e}")
        print("[DEBUG] Falling back to direct API calls for projects and labels...")
        all_projects = api.get_projects()
        all_labels_list = api.get_labels()
        print(f"[DEBUG] Fallback successful - got {len(all_projects)} projects and {len(all_labels_list)} labels")
        
    print("[DEBUG] Creating labels dictionary for quick lookup...")
    all_labels = {label.id: label.name for label in all_labels_list}
    print(f"[DEBUG] Labels dictionary created with {len(all_labels)} entries: {all_labels}")
    
    snapshot_data = []
    print(f"[DEBUG] Processing {len(all_projects)} projects...")
    
    for i, project in enumerate(all_projects):
        print(f"[DEBUG] ===========================================================")
        print(f"[DEBUG] Processing project {i+1}/{len(all_projects)}: {project.name} (ID: {project.id})")
        project_tasks = []
        
        # Flatten the paginated task results for the current project
        try:
            print(f"[DEBUG]   Attempting to get all tasks for project {project.id} with pagination...")
            tasks_iterator = api.get_tasks(project_id=project.id)
            tasks_in_project = [task for page in tasks_iterator for task in page]
            print(f"[DEBUG]   Successfully retrieved {len(tasks_in_project)} tasks via pagination")
        except TypeError as e:
            print(f"[DEBUG]   WARNING: Task pagination failed with TypeError: {e}")
            print(f"[DEBUG]   Falling back to direct task API call for project {project.id}...")
            tasks_in_project = api.get_tasks(project_id=project.id)
            print(f"[DEBUG]   Fallback successful - got {len(tasks_in_project)} tasks")
            
        for j, task in enumerate(tasks_in_project):
            print(f"[DEBUG]   -------------------------------------------------")
            print(f"[DEBUG]   Processing task {j+1}/{len(tasks_in_project)}: {task.content} (ID: {task.id})")
            task_labels = []
            
            if task.label_ids:
                print(f"[DEBUG]     Task has {len(task.label_ids)} label IDs: {task.label_ids}")
                for label_id in task.label_ids:
                    if label_id in all_labels:
                        label_name = all_labels[label_id]
                        print(f"[DEBUG]       Adding label: {label_name} (ID: {label_id})")
                        task_labels.append(
                            {"label_id": label_id, "label_name": label_name}
                        )
                    else:
                        print(f"[DEBUG]       WARNING: Label ID {label_id} not found in labels dictionary")
            else:
                print("[DEBUG]     Task has no labels")
                
            task_data = {
                "task_id": task.id,
                "task_name": task.content,
                "labels": task_labels,
            }
            project_tasks.append(task_data)
            print(f"[DEBUG]     Task data added: {task_data}")
        
        project_data = {
            "project_id": project.id,
            "project_name": project.name,
            "tasks": project_tasks,
        }
        snapshot_data.append(project_data)
        print(f"[DEBUG]   Project '{project.name}' completed with {len(project_tasks)} tasks")
    
    print("[DEBUG] ===========================================================")
    print(f"[DEBUG] Snapshot creation completed successfully!")
    print(f"[DEBUG] Total projects processed: {len(snapshot_data)}")
    total_tasks = sum(len(project['tasks']) for project in snapshot_data)
    print(f"[DEBUG] Total tasks across all projects: {total_tasks}")
    
    response = {
        "projects": snapshot_data,
        "message": f"Snapshot retrieved successfully with {len(snapshot_data)} projects.",
    }
    print(f"[DEBUG] <--- Exiting handle_get_snapshot with response summary: {response['message']}")
    return response