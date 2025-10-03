#!/usr/bin/env python3
"""
Test script for flow functionality in Auto APK Analyzer
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.task_manager import TaskManager
from utils.predefined_flows import (
    PREDEFINED_FLOWS,
    get_tasks_for_flow,
    get_subtasks_for_task
)

def test_flow_creation():
    """Test creation of predefined flows and tasks."""
    print("Testing Flow Creation")
    print("=" * 30)

    # Create task manager
    tm = TaskManager()

    # Show available flows
    print("Available Flows:")
    for flow in PREDEFINED_FLOWS:
        print(f"  - {flow['name']} ({flow['flow_id']}): {flow['description']}")

    print("\nCreating flows and tasks...")

    # Create each flow
    for flow_def in PREDEFINED_FLOWS:
        flow = tm.create_flow(flow_def["flow_id"], flow_def["name"], flow_def["description"])
        print(f"\nCreated flow: {flow.name}")

        # Get tasks for this flow
        tasks = get_tasks_for_flow(flow_def["flow_id"])
        print(f"  Flow contains {len(tasks)} tasks:")

        # Create tasks
        for task_def in tasks:
            task = tm.create_task(
                task_def["task_id"],
                task_def["name"],
                task_def["description"],
                task_def["priority"]
            )
            tm.add_task_to_flow(flow_def["flow_id"], task_def["task_id"])
            print(f"    Created task: {task.name}")

            # Check for subtasks
            subtasks = get_subtasks_for_task(task_def["task_id"])
            if subtasks:
                print(f"      Task has {len(subtasks)} subtasks:")
                for subtask_def in subtasks:
                    subtask = tm.create_task(
                        subtask_def["task_id"],
                        subtask_def["name"],
                        subtask_def["description"],
                        subtask_def["priority"],
                        parent_task_id=task_def["task_id"]
                    )
                    print(f"        Created subtask: {subtask.name}")

    # Display flow overviews
    print("\nFlow Overviews:")
    print("-" * 20)
    for flow_def in PREDEFINED_FLOWS:
        print(f"\n{flow_def['name']}:")
        tm.print_flow_overview(flow_def["flow_id"])

def test_task_management():
    """Test task management functionality."""
    print("\n\nTesting Task Management")
    print("=" * 30)

    # Create task manager
    tm = TaskManager()

    # Create a sample flow for testing
    flow = tm.create_flow("test_flow_001", "Test Flow", "Flow for testing task management")

    # Create tasks
    task1 = tm.create_task("task_001", "First Task", "First task in the flow")
    task2 = tm.create_task("task_002", "Second Task", "Second task in the flow")
    task3 = tm.create_task("task_003", "Third Task", "Third task in the flow")

    # Add tasks to flow
    tm.add_task_to_flow("test_flow_001", "task_001")
    tm.add_task_to_flow("test_flow_001", "task_002")
    tm.add_task_to_flow("test_flow_001", "task_003")

    # Create subtasks
    subtask1 = tm.create_task("subtask_001", "First Subtask", "Subtask of first task", parent_task_id="task_001")
    subtask2 = tm.create_task("subtask_002", "Second Subtask", "Another subtask of first task", parent_task_id="task_001")

    print("Initial flow state:")
    tm.print_flow_overview("test_flow_001")

    # Test task state changes
    print("\nTesting task state changes:")

    # Start a task
    tm.start_task("task_001")
    print("Started task_001")

    # Complete subtasks
    tm.complete_task("subtask_001")
    print("Completed subtask_001")

    tm.complete_task("subtask_002")
    print("Completed subtask_002")

    # Complete parent task (should auto-complete when all subtasks are done)
    print("Parent task_001 should auto-complete when all subtasks are completed")

    # Complete another task
    tm.start_task("task_002")
    tm.complete_task("task_002")
    print("Completed task_002")

    print("\nFinal flow state:")
    tm.print_flow_overview("test_flow_001")

if __name__ == "__main__":
    test_flow_creation()
    test_task_management()