#!/usr/bin/env python3
"""
Unit tests for component enumerator module
"""

import unittest
import os
from unittest.mock import patch, MagicMock

# Add src directory to Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from component.component_enumerator import (
    is_drozer_available,
    is_device_connected,
    enumerate_activities,
    enumerate_services,
    enumerate_receivers,
    enumerate_providers,
    enumerate_components
)

class TestComponentEnumerator(unittest.TestCase):
    """Test cases for component enumerator functions"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_package = "com.example.test"

    @patch('component.component_enumerator.subprocess.run')
    def test_is_drozer_available_success(self, mock_run):
        """Test Drozer availability check - success case"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = is_drozer_available()
        self.assertTrue(result)

    @patch('component.component_enumerator.subprocess.run')
    def test_is_drozer_available_failure(self, mock_run):
        """Test Drozer availability check - failure case"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = is_drozer_available()
        self.assertFalse(result)

    @patch('component.component_enumerator.subprocess.run')
    def test_is_device_connected_success(self, mock_run):
        """Test device connection check - success case"""
        mock_result = MagicMock()
        mock_result.stdout = "List of devices attached\n1234567890\tdevice\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = is_device_connected()
        self.assertTrue(result)

    @patch('component.component_enumerator.subprocess.run')
    def test_is_device_connected_failure(self, mock_run):
        """Test device connection check - failure case"""
        mock_result = MagicMock()
        mock_result.stdout = "List of devices attached\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = is_device_connected()
        self.assertFalse(result)

    @patch('component.component_enumerator.subprocess.run')
    def test_enumerate_activities(self, mock_run):
        """Test activity enumeration function"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "com.example.test.MainActivity\ncom.example.test.SettingsActivity\n"
        mock_run.return_value = mock_result

        result = enumerate_activities(self.test_package)
        self.assertIsInstance(result, list)

    @patch('component.component_enumerator.subprocess.run')
    def test_enumerate_services(self, mock_run):
        """Test service enumeration function"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "com.example.test.BackgroundService\n"
        mock_run.return_value = mock_result

        result = enumerate_services(self.test_package)
        self.assertIsInstance(result, list)

    @patch('component.component_enumerator.subprocess.run')
    def test_enumerate_receivers(self, mock_run):
        """Test receiver enumeration function"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "com.example.test.BootReceiver\n"
        mock_run.return_value = mock_result

        result = enumerate_receivers(self.test_package)
        self.assertIsInstance(result, list)

    @patch('component.component_enumerator.subprocess.run')
    def test_enumerate_providers(self, mock_run):
        """Test provider enumeration function"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "com.example.test.DataProvider\n"
        mock_run.return_value = mock_result

        result = enumerate_providers(self.test_package)
        self.assertIsInstance(result, list)

    @patch('component.component_enumerator.is_device_connected')
    @patch('component.component_enumerator.is_drozer_available')
    @patch('component.component_enumerator.start_drozer_server')
    @patch('component.component_enumerator.stop_drozer_server')
    @patch('component.component_enumerator.enumerate_activities')
    @patch('component.component_enumerator.enumerate_services')
    @patch('component.component_enumerator.enumerate_receivers')
    @patch('component.component_enumerator.enumerate_providers')
    def test_enumerate_components(self, mock_providers, mock_receivers, mock_services,
                                 mock_activities, mock_stop_server, mock_start_server,
                                 mock_drozer_available, mock_device_connected):
        """Test component enumeration function"""
        # Set up mocks
        mock_device_connected.return_value = True
        mock_drozer_available.return_value = True
        mock_start_server.return_value = MagicMock()
        mock_activities.return_value = ["MainActivity"]
        mock_services.return_value = ["BackgroundService"]
        mock_receivers.return_value = ["BootReceiver"]
        mock_providers.return_value = ["DataProvider"]

        result = enumerate_components(self.test_package)
        self.assertIsInstance(result, dict)
        self.assertIn("package", result)
        self.assertIn("activities", result)
        self.assertIn("services", result)
        self.assertIn("receivers", result)
        self.assertIn("providers", result)

if __name__ == '__main__':
    unittest.main()