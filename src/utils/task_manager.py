#!/usr/bin/env python3
"""
Task Manager for Auto APK Analyzer
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Task:
    def __init__(self, task_id: str, name: str, description: str,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 parent_task_id: Optional[str] = None):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.status = TaskStatus.PENDING
        self.priority = priority
        self.parent_task_id = parent_task_id
        self.subtasks: List[str] = []
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.assigned_to: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def start(self):
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()

    def fail(self, error_message: str = ""):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.metadata["error"] = error_message

    def add_subtask(self, subtask_id: str):
        """Add a subtask to this task."""
        if subtask_id not in self.subtasks:
            self.subtasks.append(subtask_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "assigned_to": self.assigned_to,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            task_id=data["task_id"],
            name=data["name"],
            description=data["description"],
            priority=TaskPriority(data.get("priority", 2)),
            parent_task_id=data.get("parent_task_id")
        )
        task.status = TaskStatus(data.get("status", "pending"))
        task.subtasks = data.get("subtasks", [])
        task.assigned_to = data.get("assigned_to")
        task.metadata = data.get("metadata", {})

        # Parse datetime fields
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])

        return task

class Flow:
    def __init__(self, flow_id: str, name: str, description: str):
        self.flow_id = flow_id
        self.name = name
        self.description = description
        self.tasks: List[str] = []
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.status = TaskStatus.PENDING

    def add_task(self, task_id: str):
        """Add a task to this flow."""
        if task_id not in self.tasks:
            self.tasks.append(task_id)

    def start(self):
        """Mark flow as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self):
        """Mark flow as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert flow to dictionary for serialization."""
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "description": self.description,
            "tasks": self.tasks,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Flow':
        """Create flow from dictionary."""
        flow = cls(
            flow_id=data["flow_id"],
            name=data["name"],
            description=data["description"]
        )
        flow.tasks = data.get("tasks", [])
        flow.status = TaskStatus(data.get("status", "pending"))

        # Parse datetime fields
        if data.get("created_at"):
            flow.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            flow.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            flow.completed_at = datetime.fromisoformat(data["completed_at"])

        return flow

class TaskManager:
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = workspace_path
        self.tasks_file = os.path.join(workspace_path, "tasks.json")
        self.flows_file = os.path.join(workspace_path, "flows.json")
        self.tasks: Dict[str, Task] = {}
        self.flows: Dict[str, Flow] = {}
        self.load_tasks()
        self.load_flows()

    def create_task(self, task_id: str, name: str, description: str,
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   parent_task_id: Optional[str] = None) -> Task:
        """Create a new task."""
        task = Task(task_id, name, description, priority, parent_task_id)
        self.tasks[task_id] = task

        # If this is a subtask, add it to the parent
        if parent_task_id and parent_task_id in self.tasks:
            self.tasks[parent_task_id].add_subtask(task_id)

        self.save_tasks()
        return task

    def create_flow(self, flow_id: str, name: str, description: str) -> Flow:
        """Create a new flow."""
        flow = Flow(flow_id, name, description)
        self.flows[flow_id] = flow
        self.save_flows()
        return flow

    def add_task_to_flow(self, flow_id: str, task_id: str):
        """Add a task to a flow."""
        if flow_id in self.flows and task_id in self.tasks:
            self.flows[flow_id].add_task(task_id)
            self.save_flows()

    def start_task(self, task_id: str):
        """Start a task."""
        if task_id in self.tasks:
            self.tasks[task_id].start()
            self.save_tasks()

    def complete_task(self, task_id: str):
        """Complete a task."""
        if task_id in self.tasks:
            self.tasks[task_id].complete()
            self.save_tasks()

            # Check if parent task can be completed
            self._check_parent_completion(task_id)

    def fail_task(self, task_id: str, error_message: str = ""):
        """Fail a task."""
        if task_id in self.tasks:
            self.tasks[task_id].fail(error_message)
            self.save_tasks()

    def _check_parent_completion(self, task_id: str):
        """Check if parent task can be completed (all subtasks completed)."""
        task = self.tasks[task_id]
        if task.parent_task_id and task.parent_task_id in self.tasks:
            parent_task = self.tasks[task.parent_task_id]
            # Check if all subtasks are completed
            all_completed = True
            for subtask_id in parent_task.subtasks:
                if subtask_id in self.tasks:
                    if self.tasks[subtask_id].status != TaskStatus.COMPLETED:
                        all_completed = False
                        break

            if all_completed:
                parent_task.complete()
                self.save_tasks()

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None

    def get_flow_status(self, flow_id: str) -> Optional[TaskStatus]:
        """Get the status of a flow."""
        if flow_id in self.flows:
            return self.flows[flow_id].status
        return None

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """List all tasks, optionally filtered by status."""
        if status:
            return [task for task in self.tasks.values() if task.status == status]
        return list(self.tasks.values())

    def list_flows(self, status: Optional[TaskStatus] = None) -> List[Flow]:
        """List all flows, optionally filtered by status."""
        if status:
            return [flow for flow in self.flows.values() if flow.status == status]
        return list(self.flows.values())

    def save_tasks(self):
        """Save tasks to file."""
        # Create workspace directory if it doesn't exist
        os.makedirs(self.workspace_path, exist_ok=True)

        tasks_data = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks_data, f, indent=2)

    def load_tasks(self):
        """Load tasks from file."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    tasks_data = json.load(f)
                self.tasks = {task_id: Task.from_dict(data) for task_id, data in tasks_data.items()}
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = {}

    def save_flows(self):
        """Save flows to file."""
        # Create workspace directory if it doesn't exist
        os.makedirs(self.workspace_path, exist_ok=True)

        flows_data = {flow_id: flow.to_dict() for flow_id, flow in self.flows.items()}
        with open(self.flows_file, 'w') as f:
            json.dump(flows_data, f, indent=2)

    def load_flows(self):
        """Load flows from file."""
        if os.path.exists(self.flows_file):
            try:
                with open(self.flows_file, 'r') as f:
                    flows_data = json.load(f)
                self.flows = {flow_id: Flow.from_dict(data) for flow_id, data in flows_data.items()}
            except Exception as e:
                print(f"Error loading flows: {e}")
                self.flows = {}

    def print_task_tree(self, task_id: str, indent: int = 0):
        """Print a task and its subtasks in a tree format."""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        indent_str = "  " * indent
        status_icon = {
            TaskStatus.PENDING: "○",
            TaskStatus.IN_PROGRESS: "◐",
            TaskStatus.COMPLETED: "✓",
            TaskStatus.FAILED: "✗"
        }

        print(f"{indent_str}{status_icon[task.status]} {task.name} ({task.task_id})")

        for subtask_id in task.subtasks:
            self.print_task_tree(subtask_id, indent + 1)

    def print_flow_overview(self, flow_id: str):
        """Print an overview of a flow and its tasks."""
        if flow_id not in self.flows:
            print(f"Flow {flow_id} not found")
            return

        flow = self.flows[flow_id]
        print(f"Flow: {flow.name} ({flow.flow_id})")
        print(f"Status: {flow.status.value}")
        print(f"Description: {flow.description}")
        print("Tasks:")

        for task_id in flow.tasks:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                status_icon = {
                    TaskStatus.PENDING: "○",
                    TaskStatus.IN_PROGRESS: "◐",
                    TaskStatus.COMPLETED: "✓",
                    TaskStatus.FAILED: "✗"
                }
                print(f"  {status_icon[task.status]} {task.name}")

# Example usage
if __name__ == "__main__":
    # Create task manager
    tm = TaskManager()

    # Create a flow for APK analysis
    apk_flow = tm.create_flow("apk_analysis_001", "APK Analysis Pipeline", "Complete analysis of Android APK files")

    # Create tasks for the flow
    device_scan = tm.create_task("device_scan_001", "Device Scan", "Scan connected Android device for third-party apps")
    tm.add_task_to_flow("apk_analysis_001", "device_scan_001")

    # Create subtasks for device scan
    list_packages = tm.create_task("list_packages_001", "List Packages", "List all third-party packages on device",
                                  parent_task_id="device_scan_001")
    group_developers = tm.create_task("group_devs_001", "Group by Developer", "Group apps by developer",
                                     parent_task_id="device_scan_001")
    pull_apks = tm.create_task("pull_apks_001", "Pull APKs", "Pull APK files from device",
                              parent_task_id="device_scan_001")

    # Create LLM analysis task
    llm_analysis = tm.create_task("llm_analysis_001", "LLM Analysis", "Analyze apps using LLM services")
    tm.add_task_to_flow("apk_analysis_001", "llm_analysis_001")

    # Print flow overview
    tm.print_flow_overview("apk_analysis_001")

    # Print task tree
    print("\nTask Tree:")
    tm.print_task_tree("device_scan_001")