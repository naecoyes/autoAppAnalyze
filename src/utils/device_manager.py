#!/usr/bin/env python3
"""
Device Management Utilities for Auto APK Analyzer
"""

import subprocess
import os
import re
import json

# Load configuration
config = {}
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')) as f:
        config = json.load(f)
except FileNotFoundError:
    print("Warning: config.json not found, using default paths")

# Get ADB path from config or use default
ADB_PATH = config.get('tools', {}).get('adb', 'adb')

def list_third_party_packages():
    """
    List all third-party packages installed on the connected device.

    Returns:
        list: List of package names
    """
    try:
        result = subprocess.run([ADB_PATH, 'shell', 'pm', 'list', 'packages', '-3'],
                              capture_output=True, text=True, check=True)
        packages = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                package_name = line.split(':')[1]
                packages.append(package_name)
        return packages
    except subprocess.CalledProcessError as e:
        print(f"Error listing packages: {e}")
        return []

def get_apk_path(package_name):
    """
    Get the APK path for a given package name.

    Args:
        package_name (str): Name of the package

    Returns:
        str: Path to the APK file on the device, or None if not found
    """
    try:
        result = subprocess.run([ADB_PATH, 'shell', 'pm', 'path', package_name],
                              capture_output=True, text=True, check=True)
        if result.stdout.startswith('package:'):
            apk_path = result.stdout.strip().split(':')[1]
            return apk_path
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error getting APK path for {package_name}: {e}")
        return None

def pull_apk(apk_path, local_path):
    """
    Pull an APK from the device to local storage.

    Args:
        apk_path (str): Path to the APK on the device
        local_path (str): Local path to save the APK

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        result = subprocess.run([ADB_PATH, 'pull', apk_path, local_path],
                              capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pulling APK from {apk_path}: {e}")
        return False

def is_device_connected():
    """
    Check if an Android device is connected via ADB.

    Returns:
        bool: True if device is connected, False otherwise
    """
    try:
        result = subprocess.run([ADB_PATH, 'devices'],
                              capture_output=True, text=True, check=True)
        # Check if there are any devices listed (excluding the header)
        lines = result.stdout.strip().split('\n')[1:]  # Skip "List of devices attached"
        for line in lines:
            if line.strip() and not line.startswith('*'):
                return True
        return False
    except subprocess.CalledProcessError:
        return False

def detect_flutter_app(apk_path):
    """
    Detect if an APK is a Flutter application.

    Args:
        apk_path (str): Path to the APK file

    Returns:
        bool: True if the app appears to be a Flutter application, False otherwise
    """
    # This is a simplified detection method
    # In a real implementation, we would check the APK contents
    try:
        # Check if the APK contains flutter_assets directory
        result = subprocess.run(['unzip', '-l', apk_path],
                              capture_output=True, text=True, check=True)

        # Look for flutter-related files
        if 'flutter_assets' in result.stdout or 'libflutter.so' in result.stdout:
            return True

        return False
    except subprocess.CalledProcessError:
        # If unzip fails, we can't determine if it's Flutter
        return False

def get_app_metadata(package_name):
    """
    Get metadata for an app including developer information.

    Args:
        package_name (str): Package name of the app

    Returns:
        dict: App metadata including developer info
    """
    metadata = {
        'package_name': package_name,
        'app_name': '',
        'developer': '',
        'version': ''
    }

    try:
        # Get app label/name
        result = subprocess.run([ADB_PATH, 'shell', 'dumpsys', 'package', package_name],
                              capture_output=True, text=True, check=True)

        # Parse the output to extract relevant information
        lines = result.stdout.split('\n')
        for line in lines:
            if 'applicationLabel=' in line:
                # Extract app name
                metadata['app_name'] = line.split('applicationLabel=')[1].strip()
            elif 'versionName=' in line:
                # Extract version
                metadata['version'] = line.split('versionName=')[1].strip()

        # Try to get developer information (this is often not directly available)
        # We can try to extract it from the APK path or other sources
        apk_path = get_apk_path(package_name)
        if apk_path:
            # The APK path might contain some developer information
            # This is a simplified approach
            path_parts = apk_path.split('/')
            if len(path_parts) > 2:
                # Sometimes the developer info is in the path
                metadata['developer'] = path_parts[-2]  # Just a guess

    except subprocess.CalledProcessError as e:
        print(f"Error getting metadata for {package_name}: {e}")

    return metadata

def group_apps_by_developer(packages):
    """
    Group apps by developer based on package name patterns.

    Args:
        packages (list): List of package names

    Returns:
        dict: Dictionary with developer names as keys and lists of apps as values
    """
    developer_groups = {}

    for package in packages:
        # Extract potential developer name from package name
        # This is a heuristic approach - in reality, you'd need more sophisticated methods
        parts = package.split('.')

        # Common patterns for developer identification
        if len(parts) >= 2:
            # Try to identify developer from package name structure
            # e.g., com.google.android.apps.photos -> google
            # e.g., com.whatsapp -> whatsapp
            # e.g., com.facebook.katana -> facebook

            if parts[0] == 'com' and len(parts) >= 3:
                if parts[1] in ['google', 'microsoft', 'facebook', 'twitter', 'instagram']:
                    developer = parts[1]
                else:
                    developer = parts[1] + '.' + parts[2] if len(parts) > 2 else parts[1]
            else:
                developer = parts[0]

            # Add to developer group
            if developer not in developer_groups:
                developer_groups[developer] = []
            developer_groups[developer].append(package)
        else:
            # Fallback for unusual package names
            if 'unknown' not in developer_groups:
                developer_groups['unknown'] = []
            developer_groups['unknown'].append(package)

    return developer_groups

# Example usage
if __name__ == "__main__":
    if is_device_connected():
        print("Device is connected")
        packages = list_third_party_packages()
        print(f"Found {len(packages)} third-party packages")
        if packages:
            print("Sample packages:")
            for pkg in packages[:5]:  # Show first 5 packages
                print(f"  {pkg}")
                apk_path = get_apk_path(pkg)
                if apk_path:
                    print(f"    APK Path: {apk_path}")
    else:
        print("No device connected")