#!/usr/bin/env python3
"""
Component Enumeration Module for Auto APK Analyzer
"""

import subprocess
import time
import json
import os
import re
from pathlib import Path

# Load configuration
config = {}
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')) as f:
        config = json.load(f)
except FileNotFoundError:
    print("Warning: config.json not found, using default paths")

# Get tool paths from config or use defaults
DROZER_PATH = config.get('tools', {}).get('drozer', 'drozer')
ADB_PATH = config.get('tools', {}).get('adb', 'adb')

def is_drozer_available():
    """
    Check if Drozer is available and properly configured.

    Returns:
        bool: True if Drozer is available, False otherwise
    """
    try:
        result = subprocess.run([DROZER_PATH, '--version'],
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
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

def start_drozer_server():
    """
    Start the Drozer server.

    Returns:
        subprocess.Popen: Server process if successful, None otherwise
    """
    try:
        print("Starting Drozer server...")
        # Start Drozer server in background
        server_process = subprocess.Popen([
            DROZER_PATH, 'server', 'start'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for server to start
        time.sleep(3)

        # Check if server is running
        if server_process.poll() is None:
            print("Drozer server started successfully")
            return server_process
        else:
            print("Failed to start Drozer server")
            return None

    except Exception as e:
        print(f"Error starting Drozer server: {e}")
        return None

def stop_drozer_server(server_process):
    """
    Stop the Drozer server.

    Args:
        server_process (subprocess.Popen): Server process to stop
    """
    try:
        if server_process and server_process.poll() is None:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("Drozer server stopped successfully")
    except subprocess.TimeoutExpired:
        server_process.kill()
        print("Drozer server killed forcefully")
    except Exception as e:
        print(f"Error stopping Drozer server: {e}")

def enumerate_activities(package_name):
    """
    Enumerate exported activities for a package.

    Args:
        package_name (str): Package name to enumerate

    Returns:
        list: List of exported activities
    """
    activities = []

    try:
        # Use Drozer to enumerate activities
        cmd = [
            DROZER_PATH, 'console', 'connect',
            '-c', f'run app.activity.info -a {package_name}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse the output to extract activities
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Activity' in line and package_name in line:
                    # Extract activity name
                    match = re.search(r'([a-zA-Z0-9_.]+Activity)', line)
                    if match:
                        activities.append(match.group(1))

        return activities

    except Exception as e:
        print(f"Error enumerating activities for {package_name}: {e}")
        return activities

def enumerate_services(package_name):
    """
    Enumerate exported services for a package.

    Args:
        package_name (str): Package name to enumerate

    Returns:
        list: List of exported services
    """
    services = []

    try:
        # Use Drozer to enumerate services
        cmd = [
            DROZER_PATH, 'console', 'connect',
            '-c', f'run app.service.info -a {package_name}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse the output to extract services
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Service' in line and package_name in line:
                    # Extract service name
                    match = re.search(r'([a-zA-Z0-9_.]+Service)', line)
                    if match:
                        services.append(match.group(1))

        return services

    except Exception as e:
        print(f"Error enumerating services for {package_name}: {e}")
        return services

def enumerate_receivers(package_name):
    """
    Enumerate exported broadcast receivers for a package.

    Args:
        package_name (str): Package name to enumerate

    Returns:
        list: List of exported receivers
    """
    receivers = []

    try:
        # Use Drozer to enumerate receivers
        cmd = [
            DROZER_PATH, 'console', 'connect',
            '-c', f'run app.broadcast.info -a {package_name}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse the output to extract receivers
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Receiver' in line and package_name in line:
                    # Extract receiver name
                    match = re.search(r'([a-zA-Z0-9_.]+Receiver)', line)
                    if match:
                        receivers.append(match.group(1))

        return receivers

    except Exception as e:
        print(f"Error enumerating receivers for {package_name}: {e}")
        return receivers

def enumerate_providers(package_name):
    """
    Enumerate content providers for a package.

    Args:
        package_name (str): Package name to enumerate

    Returns:
        list: List of content providers
    """
    providers = []

    try:
        # Use Drozer to enumerate content providers
        cmd = [
            DROZER_PATH, 'console', 'connect',
            '-c', f'run app.provider.info -a {package_name}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse the output to extract providers
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Content Provider' in line and package_name in line:
                    # Extract provider name
                    match = re.search(r'([a-zA-Z0-9_.]+ContentProvider)', line)
                    if match:
                        providers.append(match.group(1))

        return providers

    except Exception as e:
        print(f"Error enumerating providers for {package_name}: {e}")
        return providers

def probe_content_provider(provider_uri):
    """
    Probe a content provider URI to check accessibility.

    Args:
        provider_uri (str): Content provider URI to probe

    Returns:
        dict: Probe results
    """
    try:
        # Use Drozer to probe content provider
        cmd = [
            DROZER_PATH, 'console', 'connect',
            '-c', f'run app.provider.query {provider_uri}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        return {
            'uri': provider_uri,
            'accessible': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else result.stderr
        }

    except Exception as e:
        print(f"Error probing content provider {provider_uri}: {e}")
        return {
            'uri': provider_uri,
            'accessible': False,
            'error': str(e)
        }

def enumerate_components(package_name):
    """
    Enumerate all exported components for a package.

    Args:
        package_name (str): Package name to enumerate

    Returns:
        dict: Dictionary containing all enumerated components
    """
    if not is_device_connected():
        print("Error: No Android device connected via ADB")
        return {}

    if not is_drozer_available():
        print("Error: Drozer is not available")
        return {}

    # Start Drozer server
    server_process = start_drozer_server()
    if not server_process:
        print("Error: Failed to start Drozer server")
        return {}

    try:
        print(f"Enumerating components for {package_name}...")

        # Enumerate all component types
        activities = enumerate_activities(package_name)
        services = enumerate_services(package_name)
        receivers = enumerate_receivers(package_name)
        providers = enumerate_providers(package_name)

        # Probe content providers for accessibility
        provider_details = []
        for provider in providers:
            provider_uri = f"{package_name}.{provider}"
            probe_result = probe_content_provider(provider_uri)
            provider_details.append(probe_result)

        # Compile results
        results = {
            'package': package_name,
            'activities': activities,
            'services': services,
            'receivers': receivers,
            'providers': provider_details,
            'timestamp': time.time()
        }

        return results

    except Exception as e:
        print(f"Error enumerating components for {package_name}: {e}")
        return {}

    finally:
        # Stop Drozer server
        stop_drozer_server(server_process)

def enumerate_all_packages():
    """
    Enumerate components for all installed packages.

    Returns:
        dict: Dictionary containing components for all packages
    """
    if not is_device_connected():
        print("Error: No Android device connected via ADB")
        return {}

    try:
        # Get list of installed packages
        result = subprocess.run([ADB_PATH, 'shell', 'pm', 'list', 'packages', '-3'],
                              capture_output=True, text=True, check=True)

        packages = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                package_name = line.split(':')[1]
                packages.append(package_name)

        print(f"Found {len(packages)} third-party packages")

        # Enumerate components for each package
        all_components = {}
        for package in packages:
            print(f"Enumerating components for {package}...")
            components = enumerate_components(package)
            if components:
                all_components[package] = components

        return all_components

    except Exception as e:
        print(f"Error enumerating all packages: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    sample_package = "com.example.app"
    print("Running component enumeration...")

    # Enumerate components for a specific package
    components = enumerate_components(sample_package)
    if components:
        print("Component enumeration results:")
        print(json.dumps(components, indent=2))

    # Enumerate components for all packages
    # all_components = enumerate_all_packages()
    # if all_components:
    #     print("All components:")
    #     print(json.dumps(all_components, indent=2))