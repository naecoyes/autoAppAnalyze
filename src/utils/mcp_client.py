#!/usr/bin/env python3
"""
MCP Client for Auto APK Analyzer
"""

import json
import subprocess
import os
import time

# Load configuration
config = {}
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')) as f:
        config = json.load(f)
except FileNotFoundError:
    print("Warning: config.json not found")

class MCPClient:
    def __init__(self, server_name):
        """
        Initialize MCP client for a specific server.

        Args:
            server_name (str): Name of the MCP server to connect to
        """
        self.server_name = server_name
        self.server_config = config.get('mcp_servers', {}).get(server_name, {})
        self.process = None

    def start_server(self):
        """
        Start the MCP server process.

        Returns:
            bool: True if server started successfully, False otherwise
        """
        if not self.server_config:
            print(f"Error: No configuration found for MCP server '{self.server_name}'")
            return False

        try:
            command = self.server_config['command']
            args = self.server_config.get('args', [])

            # Start the server process
            self.process = subprocess.Popen([command] + args,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          text=True)

            # Give the server a moment to start
            time.sleep(2)

            # Check if the process is still running
            if self.process.poll() is None:
                print(f"MCP server '{self.server_name}' started successfully")
                return True
            else:
                stdout, stderr = self.process.communicate()
                print(f"Error starting MCP server '{self.server_name}': {stderr}")
                return False

        except Exception as e:
            print(f"Error starting MCP server '{self.server_name}': {e}")
            return False

    def stop_server(self):
        """
        Stop the MCP server process.
        """
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print(f"MCP server '{self.server_name}' stopped successfully")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print(f"MCP server '{self.server_name}' killed forcefully")

    def is_running(self):
        """
        Check if the MCP server is running.

        Returns:
            bool: True if server is running, False otherwise
        """
        return self.process and self.process.poll() is None

# Specific MCP clients for different tools
class JadxMCPClient(MCPClient):
    def __init__(self):
        super().__init__('jadx_mcp_server')

class MobileTestingMCPClient(MCPClient):
    def __init__(self):
        super().__init__('mobile_app_testing')

# Example usage
if __name__ == "__main__":
    # Example of starting and stopping the JADX MCP server
    jadx_client = JadxMCPClient()

    if jadx_client.start_server():
        print("JADX MCP server is running")
        # Do some work with the server...
        time.sleep(5)
        jadx_client.stop_server()
    else:
        print("Failed to start JADX MCP server")