#!/usr/bin/env python3
"""
Unit tests for static analyzer module
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add src directory to Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from static.static_analyzer import run_jadx_extraction, run_apkleaks_scan, run_mobsf_scan

class TestStaticAnalyzer(unittest.TestCase):
    """Test cases for static analyzer functions"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_apk = self.test_dir / "test.apk"
        # Create a dummy APK file for testing
        self.test_apk.touch()

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Clean up temporary files
        if self.test_apk.exists():
            self.test_apk.unlink()
        self.test_dir.rmdir()

    def test_run_jadx_extraction(self):
        """Test JADX extraction function"""
        # This is a basic test - in a real implementation, we would test with actual APK files
        result = run_jadx_extraction(str(self.test_apk))
        self.assertIsInstance(result, dict)
        self.assertIn("urls", result)
        self.assertIn("domains", result)
        self.assertIn("endpoints", result)

    def test_run_apkleaks_scan(self):
        """Test APKLeaks scan function"""
        result = run_apkleaks_scan(str(self.test_apk))
        self.assertIsInstance(result, dict)
        self.assertIn("urls", result)
        self.assertIn("endpoints", result)
        self.assertIn("secrets", result)

    def test_run_mobsf_scan(self):
        """Test MobSF scan function"""
        result = run_mobsf_scan(str(self.test_apk))
        self.assertIsInstance(result, dict)
        self.assertIn("urls", result)
        self.assertIn("domains", result)
        self.assertIn("certificates", result)
        self.assertIn("permissions", result)

if __name__ == '__main__':
    unittest.main()