#!/usr/bin/env python3
"""
Dynamic Analysis Module for Auto APK Analyzer
"""

import subprocess
import time
import json
import os
import requests
from pathlib import Path

# Load configuration
config = {}
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')) as f:
        config = json.load(f)
except FileNotFoundError:
    print("Warning: config.json not found, using default paths")

# Get tool paths from config or use defaults
FRIDA_PATH = config.get('tools', {}).get('frida', 'frida')
ADB_PATH = config.get('tools', {}).get('adb', 'adb')

def setup_reqable_capture(package_name):
    """
    Setup Reqable proxy for traffic capture.

    Args:
        package_name (str): Package name to capture traffic for

    Returns:
        bool: True if setup successful, False otherwise
    """
    # This is a placeholder implementation
    # In a real implementation, we would interact with Reqable's API or scripting engine
    print(f"Setting up Reqable capture for {package_name}")

    # For now, we'll just print the setup commands that would be needed
    print("To manually setup Reqable capture:")
    print("1. Start Reqable proxy")
    print("2. Configure device to use Reqable as HTTP proxy")
    print("3. Install Reqable CA certificate on device")
    print("4. Configure Reqable to capture traffic for specific app")

    return True

def stop_reqable_capture():
    """
    Stop Reqable traffic capture.

    Returns:
        bool: True if stopped successfully, False otherwise
    """
    # This is a placeholder implementation
    print("Stopping Reqable capture")
    return True

def run_frida_hook(package_name, script_path=None):
    """
    Run Frida hook for certificate pinning bypass.

    Args:
        package_name (str): Package name to hook
        script_path (str): Path to Frida script (optional)

    Returns:
        subprocess.Popen: Frida process if successful, None otherwise
    """
    print(f"Running Frida hook on {package_name}")

    try:
        # If no script provided, use a basic certificate pinning bypass script
        if not script_path:
            # Create a temporary script for basic certificate pinning bypass
            script_content = """
Java.perform(function() {
    var CertificateFactory = Java.use("java.security.cert.CertificateFactory");
    var TrustManagerFactory = Java.use("javax.net.ssl.TrustManagerFactory");
    var SSLContext = Java.use("javax.net.ssl.SSLContext");

    // TrustManager implementation
    var TrustManager = Java.registerClass({
        name: 'com.example.TrustManager',
        implements: [Java.use('javax.net.ssl.X509TrustManager')],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });

    // Override SSLContext.init
    SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function(keyManager, trustManager, secureRandom) {
        console.log('[*] SSLContext.init called');
        var trustManagers = [TrustManager.$new()];
        this.init(keyManager, trustManagers, secureRandom);
    };

    console.log('[*] Certificate pinning bypass loaded');
});
"""
            # Write script to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script_content)
                script_path = f.name

        print(f"Using script: {script_path}")

        # Run Frida with the script
        frida_cmd = [
            FRIDA_PATH,
            '-U',  # Connect to USB device
            '-n', package_name,
            '-l', script_path
        ]

        print(f"Executing: {' '.join(frida_cmd)}")

        # Start Frida process in background
        frida_process = subprocess.Popen(
            frida_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a moment to see if it starts successfully
        time.sleep(2)

        # Check if process is still running
        if frida_process.poll() is None:
            print("Frida hook started successfully")
            return frida_process
        else:
            stdout, stderr = frida_process.communicate()
            print(f"Frida hook failed: {stderr}")
            return None

    except Exception as e:
        print(f"Error running Frida hook: {e}")
        return None

def run_frida_flutter_hook(package_name):
    """
    Run Frida hook specifically for Flutter applications.

    Args:
        package_name (str): Package name to hook

    Returns:
        subprocess.Popen: Frida process if successful, None otherwise
    """
    print(f"Running Frida Flutter hook on {package_name}")

    try:
        # Create a script for Flutter TLS verification bypass
        # This is based on NVISO's disable-flutter-tls-verification script
        flutter_script_content = """
// Frida script to disable Flutter TLS verification
// Based on NVISO's disable-flutter-tls-verification

console.log("[*] Loading Flutter TLS bypass script");

// Wait for the Dart VM to be initialized
setTimeout(function() {
    // Try to find and hook the Dart VM functions
    try {
        // Hook for Dart SDK < 3.0
        var tls_validation_enabled = Module.findExportByName(null, "dart::bin::Builtin::TLSCertificateCallback");
        if (tls_validation_enabled) {
            Interceptor.replace(tls_validation_enabled, new NativeCallback(function() {
                console.log("[*] Bypassing Flutter TLS validation (Dart SDK < 3.0)");
                return 0; // Return false to bypass validation
            }, 'int', []));
        }

        // Hook for Dart SDK >= 3.0
        var tls_validation_new = Module.findExportByName(null, "_kDartBuiltinTLSCertificateCallback");
        if (tls_validation_new) {
            Interceptor.replace(tls_validation_new, new NativeCallback(function() {
                console.log("[*] Bypassing Flutter TLS validation (Dart SDK >= 3.0)");
                return 0; // Return false to bypass validation
            }, 'int', []));
        }

        console.log("[*] Flutter TLS bypass hooks installed");
    } catch (e) {
        console.log("[!] Error installing Flutter TLS bypass: " + e);
    }
}, 1000);
"""

        # Write script to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(flutter_script_content)
            script_path = f.name

        # Run Frida with the Flutter script
        frida_cmd = [
            FRIDA_PATH,
            '-U',  # Connect to USB device
            '-n', package_name,
            '-l', script_path
        ]

        print(f"Executing: {' '.join(frida_cmd)}")

        # Start Frida process in background
        frida_process = subprocess.Popen(
            frida_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a moment to see if it starts successfully
        time.sleep(2)

        # Check if process is still running
        if frida_process.poll() is None:
            print("Frida Flutter hook started successfully")
            return frida_process
        else:
            stdout, stderr = frida_process.communicate()
            print(f"Frida Flutter hook failed: {stderr}")
            return None

    except Exception as e:
        print(f"Error running Frida Flutter hook: {e}")
        return None

def collect_proxy_flows(duration=300):
    """
    Collect traffic flows from proxy.

    Args:
        duration (int): Duration to collect flows in seconds

    Returns:
        list: List of captured flows
    """
    # This is a placeholder implementation
    print(f"Collecting proxy flows for {duration} seconds...")
    time.sleep(2)  # Simulate collection time

    # Placeholder results
    flows = [
        {
            "method": "GET",
            "url": "https://api.example.com/v1/users/123",
            "headers": {"Authorization": "Bearer token"},
            "response_status": 200
        },
        {
            "method": "POST",
            "url": "https://api.example.com/v1/login",
            "headers": {"Content-Type": "application/json"},
            "response_status": 401
        }
    ]

    return flows

def setup_flutter_interception(package_name):
    """
    Setup interception for Flutter applications.

    Args:
        package_name (str): Package name of Flutter app

    Returns:
        bool: True if setup successful, False otherwise
    """
    print(f"Setting up Flutter interception for {package_name}")

    # This would typically involve:
    # 1. Routing traffic through ProxyDroid/VPN/iptables
    # 2. Disabling TLS verification

    print("Flutter interception setup steps:")
    print("1. Configure device to route traffic through proxy")
    print("2. Install proxy CA certificate on device")
    print("3. Run Flutter TLS verification bypass script")

    return True

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

def spawn_and_hook_app(package_name, script_path=None, is_flutter=False):
    """
    Spawn an app and hook it with Frida.

    Args:
        package_name (str): Package name of the app
        script_path (str): Path to Frida script (optional)
        is_flutter (bool): Whether the app is a Flutter app

    Returns:
        subprocess.Popen: Frida process if successful, None otherwise
    """
    if not is_device_connected():
        print("Error: No Android device connected via ADB")
        return None

    try:
        # Force stop the app first
        subprocess.run([ADB_PATH, 'shell', 'am', 'force-stop', package_name],
                      capture_output=True, check=True)

        # Spawn the app
        print(f"Spawning app: {package_name}")
        subprocess.run([ADB_PATH, 'shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'],
                      capture_output=True, check=True)

        # Wait for app to start
        time.sleep(3)

        # Run appropriate Frida hook
        if is_flutter:
            return run_frida_flutter_hook(package_name)
        else:
            return run_frida_hook(package_name, script_path)

    except Exception as e:
        print(f"Error spawning and hooking app: {e}")
        return None

# Example usage
if __name__ == "__main__":
    sample_package = "com.example.app"
    print("Running dynamic analysis modules...")

    # Setup capture
    if setup_reqable_capture(sample_package):
        print("Reqable capture setup successful")

    # Run hooks
    frida_process = run_frida_hook(sample_package)
    if frida_process:
        print("Frida hook started successfully")
        # Terminate the process after testing
        frida_process.terminate()

    # Collect flows
    flows = collect_proxy_flows(duration=30)
    print("Collected flows:", json.dumps(flows, indent=2))

    # Stop capture
    if stop_reqable_capture():
        print("Reqable capture stopped")