#!/usr/bin/env python3
"""
Unit tests for dynamic analyzer module
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from dynamic.dynamic_analyzer import (
    setup_reqable_capture,
    stop_reqable_capture,
    run_frida_hook,
    run_frida_flutter_hook,
    collect_proxy_flows,
    setup_flutter_interception,
    is_device_connected,
    spawn_and_hook_app
)

class TestDynamicAnalyzer(unittest.TestCase):
    """Test cases for dynamic analyzer functions"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_package = "com.example.test"

    def test_setup_reqable_capture(self):
        """Test Reqable capture setup function"""
        result = setup_reqable_capture(self.test_package)
        self.assertTrue(result)

    def test_stop_reqable_capture(self):
        """Test Reqable capture stop function"""
        result = stop_reqable_capture()
        self.assertTrue(result)

    def test_setup_flutter_interception(self):
        """Test Flutter interception setup function"""
        result = setup_flutter_interception(self.test_package)
        self.assertTrue(result)

    @patch('dynamic.dynamic_analyzer.subprocess.run')
    def test_is_device_connected_success(self, mock_run):
        """Test device connection check - success case"""
        # Mock successful ADB devices command
        mock_result = MagicMock()
        mock_result.stdout = "List of devices attached\n1234567890\tdevice\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = is_device_connected()
        self.assertTrue(result)

    @patch('dynamic.dynamic_analyzer.subprocess.run')
    def test_is_device_connected_failure(self, mock_run):
        """Test device connection check - failure case"""
        # Mock failed ADB devices command
        mock_result = MagicMock()
        mock_result.stdout = "List of devices attached\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = is_device_connected()
        self.assertFalse(result)

    @patch('dynamic.dynamic_analyzer.subprocess.Popen')
    @patch('dynamic.dynamic_analyzer.time.sleep')
    def test_run_frida_hook_success(self, mock_sleep, mock_popen):
        """Test Frida hook function - success case"""
        # Mock successful Frida process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is still running
        mock_popen.return_value = mock_process

        result = run_frida_hook(self.test_package)
        self.assertIsNotNone(result)
        self.assertEqual(result, mock_process)

    @patch('dynamic.dynamic_analyzer.subprocess.Popen')
    @patch('dynamic.dynamic_analyzer.time.sleep')
    def test_run_frida_hook_failure(self, mock_sleep, mock_popen):
        """Test Frida hook function - failure case"""
        # Mock failed Frida process
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process has terminated
        mock_process.communicate.return_value = ("", "Error message")
        mock_popen.return_value = mock_process

        result = run_frida_hook(self.test_package)
        self.assertIsNone(result)

    def test_collect_proxy_flows(self):
        """Test proxy flow collection function"""
        result = collect_proxy_flows(duration=5)
        self.assertIsInstance(result, list)
        # Check that we get some flow data
        self.assertGreater(len(result), 0)
        # Check structure of flow data
        flow = result[0]
        self.assertIn("method", flow)
        self.assertIn("url", flow)
        self.assertIn("headers", flow)
        self.assertIn("response_status", flow)

if __name__ == '__main__':
    unittest.main()