#!/usr/bin/env python3
"""
Flutter Application Handler for Auto APK Analyzer
"""

import subprocess
import time
import json
import os
import zipfile
from pathlib import Path

# Load configuration
config = {}
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')) as f:
        config = json.load(f)
except FileNotFoundError:
    print("Warning: config.json not found, using default paths")

# Get tool paths from config or use defaults
ADB_PATH = config.get('tools', {}).get('adb', 'adb')

def is_flutter_app(apk_path):
    """
    Detect if an APK is a Flutter application.

    Args:
        apk_path (str): Path to the APK file

    Returns:
        bool: True if the app appears to be a Flutter application, False otherwise
    """
    try:
        # Check if the APK contains flutter_assets directory or libflutter.so
        with zipfile.ZipFile(apk_path, 'r') as apk:
            # List all files in the APK
            files = apk.namelist()

            # Check for Flutter indicators
            has_flutter_assets = any('assets/flutter_assets' in f for f in files)
            has_libflutter = any('libflutter.so' in f for f in files)
            has_flutter_activity = False

            # Check for Flutter-related classes in the manifest or code
            # This is a simplified check - in a real implementation, we would parse the manifest
            flutter_indicators = [
                'io.flutter',
                'FlutterActivity',
                'FlutterFragment',
                'FlutterApplication'
            ]

            # Check if any file contains Flutter indicators
            for f in files:
                if f.endswith(('.xml', '.dex')):
                    try:
                        with apk.open(f) as file_content:
                            content = file_content.read().decode('utf-8', errors='ignore')
                            if any(indicator in content for indicator in flutter_indicators):
                                has_flutter_activity = True
                                break
                    except:
                        continue

            return has_flutter_assets or has_libflutter or has_flutter_activity

    except Exception as e:
        print(f"Error detecting Flutter app: {e}")
        return False

def setup_flutter_interception(package_name):
    """
    Setup interception for Flutter applications.

    Args:
        package_name (str): Package name of Flutter app

    Returns:
        bool: True if setup successful, False otherwise
    """
    print(f"Setting up Flutter interception for {package_name}")

    try:
        # Configure device to route traffic through proxy
        # This would typically involve:
        # 1. Setting up a proxy (like Charles or Burp)
        # 2. Installing the proxy's CA certificate on the device
        # 3. Configuring network settings

        print("Flutter interception setup steps:")
        print("1. Configure device to route traffic through proxy")
        print("2. Install proxy CA certificate on device")
        print("3. Run Flutter TLS verification bypass script")

        # For now, we'll just print the instructions
        # In a real implementation, we would automate these steps
        return True

    except Exception as e:
        print(f"Error setting up Flutter interception: {e}")
        return False

def run_flutter_tls_bypass(package_name):
    """
    Run TLS verification bypass for Flutter applications.

    Args:
        package_name (str): Package name of Flutter app

    Returns:
        subprocess.Popen: Frida process if successful, None otherwise
    """
    print(f"Running Flutter TLS bypass on {package_name}")

    try:
        # Import the dynamic analyzer module for Frida functionality
        from ..dynamic.dynamic_analyzer import run_frida_flutter_hook

        # Run the Flutter-specific Frida hook
        frida_process = run_frida_flutter_hook(package_name)

        if frida_process:
            print("Flutter TLS bypass started successfully")
            return frida_process
        else:
            print("Failed to start Flutter TLS bypass")
            return None

    except Exception as e:
        print(f"Error running Flutter TLS bypass: {e}")
        return None

def setup_proxy_routing(device_ip, proxy_port=8080):
    """
    Setup proxy routing for Flutter apps.

    Args:
        device_ip (str): IP address of the Android device
        proxy_port (int): Proxy port number

    Returns:
        bool: True if setup successful, False otherwise
    """
    try:
        print(f"Setting up proxy routing to {device_ip}:{proxy_port}")

        # Configure Wi-Fi proxy settings on the device
        # This is a simplified example - in practice, this would be more complex
        proxy_setup_commands = [
            ['adb', 'shell', 'settings', 'put', 'global', 'http_proxy', f'{device_ip}:{proxy_port}'],
            ['adb', 'shell', 'settings', 'put', 'global', 'https_proxy', f'{device_ip}:{proxy_port}']
        ]

        for cmd in proxy_setup_commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Failed to execute command {' '.join(cmd)}")

        print("Proxy routing configured")
        return True

    except Exception as e:
        print(f"Error setting up proxy routing: {e}")
        return False

def disable_proxy_routing():
    """
    Disable proxy routing on the device.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("Disabling proxy routing")

        # Disable proxy settings
        proxy_disable_commands = [
            ['adb', 'shell', 'settings', 'put', 'global', 'http_proxy', ':0'],
            ['adb', 'shell', 'settings', 'put', 'global', 'https_proxy', ':0']
        ]

        for cmd in proxy_disable_commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Failed to execute command {' '.join(cmd)}")

        print("Proxy routing disabled")
        return True

    except Exception as e:
        print(f"Error disabling proxy routing: {e}")
        return False

def handle_flutter_app(package_name, apk_path, mode='frida'):
    """
    Handle a Flutter application with appropriate interception methods.

    Args:
        package_name (str): Package name of the Flutter app
        apk_path (str): Path to the APK file
        mode (str): Interception mode ('frida' or 'repackage')

    Returns:
        dict: Results of the handling process
    """
    print(f"Handling Flutter app: {package_name}")

    results = {
        'package': package_name,
        'is_flutter': is_flutter_app(apk_path),
        'mode': mode,
        'interception_setup': False,
        'tls_bypass': False,
        'proxy_routing': False
    }

    if not results['is_flutter']:
        print(f"Warning: {package_name} does not appear to be a Flutter app")
        return results

    try:
        # Setup interception
        if setup_flutter_interception(package_name):
            results['interception_setup'] = True
            print("Flutter interception setup completed")

        # Setup proxy routing
        # Get device IP (simplified - in practice, you'd get the actual device IP)
        device_ip = "192.168.1.100"  # Placeholder
        if setup_proxy_routing(device_ip):
            results['proxy_routing'] = True
            print("Proxy routing setup completed")

        # Run TLS bypass based on mode
        if mode == 'frida':
            frida_process = run_flutter_tls_bypass(package_name)
            if frida_process:
                results['tls_bypass'] = True
                print("Frida TLS bypass started")
                # In a real implementation, you would manage this process
                # For now, we'll just terminate it for testing
                frida_process.terminate()
        elif mode == 'repackage':
            print("Repackaging mode selected - this requires signing the app")
            # In a real implementation, we would implement reFlutter or similar
            print("Repackaging not implemented in this version")

        return results

    except Exception as e:
        print(f"Error handling Flutter app: {e}")
        return results

# Example usage
if __name__ == "__main__":
    sample_package = "com.example.flutterapp"
    sample_apk = "/path/to/sample.apk"
    print("Running Flutter app handler...")

    # Handle Flutter app
    results = handle_flutter_app(sample_package, sample_apk, mode='frida')
    print("Flutter handling results:")
    print(json.dumps(results, indent=2))