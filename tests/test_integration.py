#!/usr/bin/env python3
"""
Integration tests for the Auto APK Analyzer
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.device_manager import list_third_party_packages, get_apk_path, pull_apk
from utils.workspace_manager import WorkspaceManager
from static.static_analyzer import run_jadx_extraction, run_apkleaks_scan
from dynamic.dynamic_analyzer import setup_reqable_capture, stop_reqable_capture
from component.component_enumerator import enumerate_components
from mapping.url_mapper import generate_url_map

class TestIntegration(unittest.TestCase):
    """Integration tests for the Auto APK Analyzer"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_apk = self.test_dir / "test.apk"
        # Create a dummy APK file for testing
        self.test_apk.touch()
        self.test_package = "com.example.test"

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Clean up temporary files
        if self.test_apk.exists():
            self.test_apk.unlink()
        self.test_dir.rmdir()

    @patch('utils.device_manager.subprocess.run')
    def test_device_analysis_flow(self, mock_run):
        """Test the complete device analysis flow"""
        # Mock ADB commands
        mock_result = MagicMock()
        mock_result.stdout = "package:com.example.app1\npackage:com.example.app2\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Test listing packages
        packages = list_third_party_packages()
        self.assertIsInstance(packages, list)
        self.assertGreater(len(packages), 0)

    def test_workspace_management_flow(self):
        """Test workspace management flow"""
        # Create workspace manager
        workspace_manager = WorkspaceManager(str(self.test_dir / "workspace"))

        # Test creating developer workspace
        dev_workspace = workspace_manager.create_developer_workspace("test_developer")
        self.assertTrue(Path(dev_workspace).exists())

        # Test organizing APKs by developer
        developer_groups = {
            "test_developer": [self.test_package]
        }
        workspaces = workspace_manager.organize_apks_by_developer(developer_groups)
        self.assertIn("test_developer", workspaces)

    def test_static_analysis_flow(self):
        """Test static analysis flow"""
        # Test JADX extraction
        jadx_results = run_jadx_extraction(str(self.test_apk))
        self.assertIsInstance(jadx_results, dict)
        self.assertIn("urls", jadx_results)

        # Test APKLeaks scan
        apkleaks_results = run_apkleaks_scan(str(self.test_apk))
        self.assertIsInstance(apkleaks_results, dict)
        self.assertIn("urls", apkleaks_results)

    def test_dynamic_analysis_flow(self):
        """Test dynamic analysis flow"""
        # Test Reqable capture setup
        setup_result = setup_reqable_capture(self.test_package)
        self.assertTrue(setup_result)

        # Test Reqable capture stop
        stop_result = stop_reqable_capture()
        self.assertTrue(stop_result)

    @patch('component.component_enumerator.is_device_connected')
    @patch('component.component_enumerator.is_drozer_available')
    def test_component_enumeration_flow(self, mock_drozer_available, mock_device_connected):
        """Test component enumeration flow"""
        # Mock device and drozer availability
        mock_device_connected.return_value = True
        mock_drozer_available.return_value = True

        # Test component enumeration (this will fail gracefully since we don't have a real device)
        try:
            components = enumerate_components(self.test_package)
            # Should return an empty dict or handle the error gracefully
            self.assertIsInstance(components, dict)
        except Exception as e:
            # If there's an exception, it should be handled gracefully
            self.fail(f"enumerate_components raised an exception: {e}")

    def test_url_mapping_flow(self):
        """Test URL mapping flow"""
        # Sample static results
        static_results = {
            "urls": [
                {
                    "url": "https://api.example.com/v1/users/123",
                    "original_url": "https://api.example.com/v1/users/123",
                    "parameters": [{"type": "numeric_id", "value": "123"}],
                    "sources": ["jadx"]
                }
            ],
            "domains": ["api.example.com"]
        }

        # Sample dynamic results
        dynamic_results = [
            {
                "method": "GET",
                "url": "https://api.example.com/v1/users/456",
                "headers": {"Authorization": "Bearer token"},
                "response_status": 200
            }
        ]

        # Test URL map generation
        url_map = generate_url_map(static_results, dynamic_results)
        self.assertIsInstance(url_map, dict)
        self.assertIn("entries", url_map)
        self.assertIn("domains", url_map)

if __name__ == '__main__':
    unittest.main()