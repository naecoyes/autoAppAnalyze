#!/usr/bin/env python3
"""
Unit tests for Flutter handler module
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flutter.flutter_handler import (
    is_flutter_app,
    setup_flutter_interception,
    run_flutter_tls_bypass,
    setup_proxy_routing,
    disable_proxy_routing,
    handle_flutter_app
)

class TestFlutterHandler(unittest.TestCase):
    """Test cases for Flutter handler functions"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_apk = self.test_dir / "test.apk"
        # Create a dummy APK file for testing
        self.test_apk.touch()
        self.test_package = "com.example.flutterapp"

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Clean up temporary files
        if self.test_apk.exists():
            self.test_apk.unlink()
        self.test_dir.rmdir()

    def test_is_flutter_app_false(self):
        """Test Flutter app detection - false case"""
        # For this test, we'll just check that the function runs without error
        # A real test would require a proper APK file
        try:
            result = is_flutter_app(str(self.test_apk))
            # Should return False for a dummy APK
            self.assertFalse(result)
        except Exception as e:
            # If there's an exception, it should be handled gracefully
            self.fail(f"is_flutter_app raised an exception: {e}")

    def test_setup_flutter_interception(self):
        """Test Flutter interception setup function"""
        result = setup_flutter_interception(self.test_package)
        self.assertTrue(result)

    @patch('flutter.flutter_handler.subprocess.run')
    def test_setup_proxy_routing(self, mock_run):
        """Test proxy routing setup function"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = setup_proxy_routing("192.168.1.100", 8080)
        self.assertTrue(result)

    @patch('flutter.flutter_handler.subprocess.run')
    def test_disable_proxy_routing(self, mock_run):
        """Test proxy routing disable function"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = disable_proxy_routing()
        self.assertTrue(result)

    @patch('flutter.flutter_handler.is_flutter_app')
    @patch('flutter.flutter_handler.setup_flutter_interception')
    @patch('flutter.flutter_handler.setup_proxy_routing')
    def test_handle_flutter_app(self, mock_setup_proxy, mock_setup_interception, mock_is_flutter):
        """Test Flutter app handling function"""
        # Mock the functions to return success
        mock_is_flutter.return_value = True
        mock_setup_interception.return_value = True
        mock_setup_proxy.return_value = True

        result = handle_flutter_app(self.test_package, str(self.test_apk), mode='frida')
        self.assertIsInstance(result, dict)
        self.assertIn("package", result)
        self.assertIn("is_flutter", result)
        self.assertIn("mode", result)
        self.assertTrue(result["is_flutter"])

if __name__ == '__main__':
    unittest.main()