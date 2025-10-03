#!/usr/bin/env python3
"""
Workspace Manager for Auto APK Analyzer
"""

import os
import json
import shutil
from pathlib import Path

class WorkspaceManager:
    def __init__(self, base_path="./workspace"):
        """
        Initialize workspace manager.

        Args:
            base_path (str): Base path for the workspace
        """
        self.base_path = Path(base_path)
        self.apk_dir = self.base_path / "apks"
        self.results_dir = self.base_path / "results"
        self.logs_dir = self.base_path / "logs"
        self.create_directories()

    def create_directories(self):
        """Create necessary directories for the workspace."""
        directories = [self.base_path, self.apk_dir, self.results_dir, self.logs_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_developer_workspace(self, developer_name):
        """
        Create a workspace for a specific developer.

        Args:
            developer_name (str): Name of the developer

        Returns:
            Path: Path to the developer's workspace
        """
        dev_workspace = self.apk_dir / developer_name
        dev_workspace.mkdir(exist_ok=True)
        return dev_workspace

    def organize_apks_by_developer(self, developer_groups):
        """
        Organize APKs by developer in the workspace.

        Args:
            developer_groups (dict): Dictionary with developer names as keys and lists of packages as values

        Returns:
            dict: Dictionary with developer names as keys and paths to their workspaces as values
        """
        workspaces = {}

        for developer, packages in developer_groups.items():
            # Create developer workspace
            dev_workspace = self.create_developer_workspace(developer)
            workspaces[developer] = str(dev_workspace)

            print(f"Created workspace for developer: {developer}")
            print(f"  Location: {dev_workspace}")
            print(f"  Number of apps: {len(packages)}")

        return workspaces

    def get_developer_workspaces(self):
        """
        Get all existing developer workspaces.

        Returns:
            dict: Dictionary with developer names as keys and workspace paths as values
        """
        workspaces = {}
        if self.apk_dir.exists():
            for item in self.apk_dir.iterdir():
                if item.is_dir():
                    workspaces[item.name] = str(item)
        return workspaces

    def save_analysis_results(self, developer, app_package, results):
        """
        Save analysis results for a specific app.

        Args:
            developer (str): Developer name
            app_package (str): App package name
            results (dict): Analysis results
        """
        dev_results_dir = self.results_dir / developer
        dev_results_dir.mkdir(exist_ok=True)

        results_file = dev_results_dir / f"{app_package}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Saved results for {app_package} to {results_file}")

    def save_log(self, log_name, content):
        """
        Save log content to a file.

        Args:
            log_name (str): Name of the log file
            content (str): Log content
        """
        log_file = self.logs_dir / f"{log_name}.log"
        with open(log_file, 'w') as f:
            f.write(content)

        print(f"Saved log to {log_file}")

# Example usage
if __name__ == "__main__":
    # Create workspace manager
    wm = WorkspaceManager()

    # Example developer groups
    developer_groups = {
        "google": ["com.google.android.apps.photos", "com.google.android.apps.maps"],
        "facebook": ["com.facebook.katana", "com.facebook.orca"],
        "unknown": ["com.example.app1", "com.example.app2"]
    }

    # Organize APKs by developer
    workspaces = wm.organize_apks_by_developer(developer_groups)

    print("\nWorkspaces created:")
    for dev, path in workspaces.items():
        print(f"  {dev}: {path}")

    # Get existing workspaces
    existing_workspaces = wm.get_developer_workspaces()
    print("\nExisting workspaces:")
    for dev, path in existing_workspaces.items():
        print(f"  {dev}: {path}")