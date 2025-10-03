#!/usr/bin/env python3
"""
Auto APK Analyzer - Main Entry Point
"""

import argparse
import os
import sys
import json
import time
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.device_manager import (
    is_device_connected,
    list_third_party_packages,
    get_apk_path,
    pull_apk,
    group_apps_by_developer,
    detect_flutter_app
)
from utils.workspace_manager import WorkspaceManager
from utils.llm_client import AppDiscoveryClient
from utils.task_manager import TaskManager
from utils.predefined_flows import (
    get_flow_definition,
    get_tasks_for_flow,
    get_subtasks_for_task
)

# Import analysis modules
from static.static_analyzer import run_jadx_extraction, run_apkleaks_scan, run_mobsf_scan
from dynamic.dynamic_analyzer import spawn_and_hook_app, setup_reqable_capture, stop_reqable_capture, collect_proxy_flows
from component.component_enumerator import enumerate_components
from flutter.flutter_handler import is_flutter_app, handle_flutter_app
from mapping.url_mapper import generate_url_map, save_url_map
from utils.url_normalizer import merge_static_results

def analyze_device_apps():
    """Analyze apps on connected device and organize by developer."""
    print("Auto APK Analyzer - Device Analysis Mode")
    print("========================================")

    # Check if device is connected
    if not is_device_connected():
        print("Error: No Android device connected via ADB")
        return False

    print("Device connected successfully")

    # Create workspace manager
    workspace_manager = WorkspaceManager()

    # List third-party packages
    print("Listing third-party packages...")
    packages = list_third_party_packages()

    if not packages:
        print("No third-party packages found")
        return False

    print(f"Found {len(packages)} third-party packages")

    # Group apps by developer
    print("Grouping apps by developer...")
    developer_groups = group_apps_by_developer(packages)

    print(f"Grouped into {len(developer_groups)} developer groups:")
    for developer, app_list in developer_groups.items():
        print(f"  {developer}: {len(app_list)} apps")

    # Create workspaces for each developer
    print("Creating workspaces...")
    workspaces = workspace_manager.organize_apks_by_developer(developer_groups)

    # Pull APKs for each developer group and analyze them
    print("Pulling and analyzing APKs...")
    for developer, app_list in developer_groups.items():
        print(f"Processing apps for developer: {developer}")
        dev_workspace = Path(workspaces[developer])

        for package in app_list:
            print(f"  Processing {package}...")
            apk_path = get_apk_path(package)

            if apk_path:
                local_apk_path = dev_workspace / f"{package}.apk"
                if pull_apk(apk_path, str(local_apk_path)):
                    print(f"    Successfully pulled {package}")
                    # Analyze the APK
                    analyze_apk(str(local_apk_path), package, dev_workspace)
                else:
                    print(f"    Failed to pull {package}")
            else:
                print(f"    Failed to get APK path for {package}")

    print("\nDevice analysis complete!")
    print(f"Workspaces created at: {workspace_manager.base_path}")
    return True

def analyze_apk(apk_path, package_name, workspace_dir):
    """
    Perform complete analysis on a single APK.

    Args:
        apk_path (str): Path to the APK file
        package_name (str): Package name of the app
        workspace_dir (Path): Workspace directory for results
    """
    print(f"    Analyzing APK: {apk_path}")

    try:
        # Create results directory for this app
        app_results_dir = workspace_dir / f"{package_name}_results"
        app_results_dir.mkdir(exist_ok=True)

        # Detect if app is Flutter-based
        is_flutter = is_flutter_app(apk_path)
        print(f"    Flutter app detected: {is_flutter}")

        # Static Analysis
        print("    Running static analysis...")
        jadx_results = run_jadx_extraction(apk_path)
        apkleaks_results = run_apkleaks_scan(apk_path)
        mobsf_results = run_mobsf_scan(apk_path)

        # Merge static analysis results
        static_results = merge_static_results(jadx_results, apkleaks_results, mobsf_results)

        # Save static analysis results
        static_results_file = app_results_dir / "static_results.json"
        with open(static_results_file, 'w') as f:
            json.dump(static_results, f, indent=2)

        # Dynamic Analysis
        dynamic_results = []
        component_results = {}

        if is_flutter:
            # Special handling for Flutter apps
            print("    Setting up Flutter interception...")
            flutter_results = handle_flutter_app(package_name, apk_path, mode='frida')

            # Run dynamic analysis with Flutter hooks
            frida_process = spawn_and_hook_app(package_name, is_flutter=True)
            if frida_process:
                # Collect traffic flows
                flows = collect_proxy_flows(duration=60)
                dynamic_results.extend(flows)
                frida_process.terminate()
        else:
            # Standard Android app handling
            print("    Setting up standard interception...")
            if setup_reqable_capture(package_name):
                # Run Frida hook for certificate pinning bypass
                frida_process = spawn_and_hook_app(package_name)
                if frida_process:
                    # Collect traffic flows
                    flows = collect_proxy_flows(duration=60)
                    dynamic_results.extend(flows)
                    frida_process.terminate()
                    stop_reqable_capture()

        # Component Enumeration
        print("    Running component enumeration...")
        component_results = enumerate_components(package_name)

        # Generate URL Map
        print("    Generating URL map...")
        url_map = generate_url_map(static_results, dynamic_results, component_results)

        # Save URL map
        url_map_file = app_results_dir / "url_map.json"
        save_url_map(url_map, str(url_map_file))

        print(f"    Analysis complete for {package_name}")
        print(f"    Results saved to: {app_results_dir}")

    except Exception as e:
        print(f"    Error analyzing APK {apk_path}: {e}")

def discover_apps_with_llm(query):
    """Discover apps using LLM services."""
    print("Auto APK Analyzer - LLM App Discovery Mode")
    print("==========================================")

    print(f"Discovering apps based on query: {query}")

    # Create app discovery client
    discovery_client = AppDiscoveryClient()

    # Show which services are configured
    print("\nConfigured LLM Services:")
    configured_services = []
    for service_name, client in discovery_client.clients.items():
        if client.is_configured:
            print(f"  {service_name}: Configured")
            configured_services.append(service_name)
        else:
            print(f"  {service_name}: Not configured")

    if not configured_services:
        print("\nNo LLM services configured. Please add API keys to api_keys.json")
        return False

    # Perform app discovery
    print(f"\nQuerying configured services: {', '.join(configured_services)}")
    results = discovery_client.discover_apps(query)

    # Display results
    for service, result in results.items():
        print(f"\n{service.upper()} Results:")
        print("-" * (len(service) + 9))
        print(result)
        print()

    return True

def create_and_execute_flow(flow_id):
    """Create and execute a predefined flow."""
    print(f"Auto APK Analyzer - Executing Flow: {flow_id}")
    print("=" * 50)

    # Initialize task manager
    task_manager = TaskManager()

    # Get flow definition
    flow_def = get_flow_definition(flow_id)
    if not flow_def:
        print(f"Error: Flow '{flow_id}' not found")
        return False

    # Create the flow
    flow = task_manager.create_flow(flow_def["flow_id"], flow_def["name"], flow_def["description"])
    print(f"Created flow: {flow.name}")

    # Get tasks for this flow
    tasks = get_tasks_for_flow(flow_id)
    print(f"Flow contains {len(tasks)} tasks")

    # Create tasks
    for task_def in tasks:
        task = task_manager.create_task(
            task_def["task_id"],
            task_def["name"],
            task_def["description"],
            task_def["priority"]
        )
        task_manager.add_task_to_flow(flow_id, task_def["task_id"])
        print(f"  Created task: {task.name}")

        # Check for subtasks
        subtasks = get_subtasks_for_task(task_def["task_id"])
        for subtask_def in subtasks:
            subtask = task_manager.create_task(
                subtask_def["task_id"],
                subtask_def["name"],
                subtask_def["description"],
                subtask_def["priority"],
                parent_task_id=task_def["task_id"]
            )
            print(f"    Created subtask: {subtask.name}")

    # Display flow overview
    task_manager.print_flow_overview(flow_id)

    # Execute the flow (simplified implementation)
    print(f"\nExecuting flow '{flow.name}'...")
    execute_flow(flow_id, task_manager)

    return True

def execute_flow(flow_id, task_manager):
    """
    Execute a predefined flow.

    Args:
        flow_id (str): ID of the flow to execute
        task_manager (TaskManager): Task manager instance
    """
    if flow_id == "device_analysis":
        analyze_device_apps()
    elif flow_id == "llm_discovery":
        # This would require a query parameter
        print("LLM discovery flow requires a query. Use --query parameter with --mode llm")
    else:
        print(f"Flow execution for '{flow_id}' not yet implemented")

def main():
    parser = argparse.ArgumentParser(description='Auto APK Analyzer - Discover hidden mobile APIs')
    parser.add_argument('--input', '-i', help='Path to APK file or directory containing APKs')
    parser.add_argument('--package', '-p', help='Package name for device-based analysis')
    parser.add_argument('--query', '-q', help='Query for LLM-based app discovery')
    parser.add_argument('--flow', '-f', help='Execute a predefined analysis flow')
    parser.add_argument('--output', '-o', help='Output directory for results')
    parser.add_argument('--mode', '-m', choices=['static', 'dynamic', 'full', 'device', 'llm'],
                        default='device', help='Analysis mode')
    parser.add_argument('--duration', '-d', type=int, default=300,
                        help='Duration for dynamic analysis in seconds')

    args = parser.parse_args()

    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    print("Auto APK Analyzer")
    print("=================")

    # Flow execution mode
    if args.flow:
        return create_and_execute_flow(args.flow)

    # LLM discovery mode
    if args.mode == 'llm':
        if not args.query:
            print("Error: --query is required for LLM discovery mode")
            return False
        return discover_apps_with_llm(args.query)

    # Device analysis mode
    if args.mode == 'device' or (not args.input and not args.package):
        return analyze_device_apps()

    # File-based analysis
    if args.input:
        if os.path.isfile(args.input) and args.input.endswith('.apk'):
            print(f"Analyzing single APK: {args.input}")
            # Create a temporary workspace
            workspace = Path("./workspace/single_apk")
            workspace.mkdir(parents=True, exist_ok=True)
            analyze_apk(args.input, "single_apk", workspace)
        elif os.path.isdir(args.input):
            print(f"Analyzing APKs in directory: {args.input}")
            # Analyze all APKs in the directory
            for file in os.listdir(args.input):
                if file.endswith('.apk'):
                    apk_path = os.path.join(args.input, file)
                    workspace = Path("./workspace/batch_analysis")
                    workspace.mkdir(parents=True, exist_ok=True)
                    analyze_apk(apk_path, file.replace('.apk', ''), workspace)
        else:
            print("Error: --input must be a valid APK file or directory")
            return False

    print("\nAnalysis complete.")
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)