#!/usr/bin/env python3
"""
Unit tests for URL mapper module
"""

import unittest
import tempfile
import os
import json
from pathlib import Path

# Add src directory to Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mapping.url_mapper import (
    create_url_mapping_entry,
    merge_static_dynamic_data,
    generate_url_map,
    save_url_map,
    load_url_map,
    compare_url_maps
)

class TestUrlMapper(unittest.TestCase):
    """Test cases for URL mapper functions"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "test_map.json"

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Clean up temporary files
        if self.test_file.exists():
            self.test_file.unlink()
        self.test_dir.rmdir()

    def test_create_url_mapping_entry(self):
        """Test URL mapping entry creation"""
        url = "https://api.example.com/v1/users/123"
        entry = create_url_mapping_entry(url, method="GET", source="static")

        self.assertIsInstance(entry, dict)
        self.assertIn("signature", entry)
        self.assertIn("host", entry)
        self.assertIn("path", entry)
        self.assertIn("method", entry)
        self.assertIn("parameters", entry)
        self.assertIn("sources", entry)
        self.assertIn("original_urls", entry)
        self.assertIn("risk_level", entry)
        self.assertEqual(entry["method"], "GET")
        self.assertIn("static", entry["sources"])
        self.assertIn(url, entry["original_urls"])

    def test_merge_static_dynamic_data(self):
        """Test merging of static and dynamic data"""
        static_results = {
            "urls": [
                {
                    "url": "https://api.example.com/v1/users/123",
                    "original_url": "https://api.example.com/v1/users/123",
                    "parameters": [{"type": "numeric_id", "value": "123"}],
                    "sources": ["jadx"]
                }
            ],
            "domains": ["api.example.com"],
            "endpoints": ["/api/v1/login"]
        }

        dynamic_results = [
            {
                "method": "GET",
                "url": "https://api.example.com/v1/users/456",
                "headers": {"Authorization": "Bearer token"},
                "response_status": 200
            }
        ]

        merged = merge_static_dynamic_data(static_results, dynamic_results)
        self.assertIsInstance(merged, dict)
        self.assertIn("entries", merged)
        self.assertIn("domains", merged)
        self.assertIn("endpoints", merged)

    def test_generate_url_map(self):
        """Test URL map generation"""
        static_results = {
            "urls": [
                {
                    "url": "https://api.example.com/v1/users/123",
                    "original_url": "https://api.example.com/v1/users/123",
                    "parameters": [{"type": "numeric_id", "value": "123"}],
                    "sources": ["jadx"]
                }
            ],
            "domains": ["api.example.com"],
            "endpoints": ["/api/v1/login"]
        }

        dynamic_results = [
            {
                "method": "GET",
                "url": "https://api.example.com/v1/users/456",
                "headers": {"Authorization": "Bearer token"},
                "response_status": 200
            }
        ]

        url_map = generate_url_map(static_results, dynamic_results)
        self.assertIsInstance(url_map, dict)
        self.assertIn("metadata", url_map)
        self.assertIn("entries", url_map)
        self.assertIn("domains", url_map)

    def test_save_and_load_url_map(self):
        """Test saving and loading URL maps"""
        url_map = {
            "entries": [
                {
                    "signature": "api.example.com/v1/users/{id}",
                    "host": "api.example.com",
                    "path": "/v1/users/{id}",
                    "method": "GET",
                    "parameters": [{"type": "numeric_id", "value": "123"}],
                    "sources": ["static"],
                    "original_urls": ["https://api.example.com/v1/users/123"],
                    "risk_level": "LOW"
                }
            ],
            "domains": ["api.example.com"]
        }

        # Test saving
        result = save_url_map(url_map, str(self.test_file))
        self.assertTrue(result)
        self.assertTrue(self.test_file.exists())

        # Test loading
        loaded_map = load_url_map(str(self.test_file))
        self.assertIsInstance(loaded_map, dict)
        self.assertIn("entries", loaded_map)
        self.assertIn("domains", loaded_map)

    def test_compare_url_maps(self):
        """Test URL map comparison"""
        old_map = {
            "entries": [
                {
                    "signature": "api.example.com/v1/users",
                    "host": "api.example.com",
                    "path": "/v1/users",
                    "method": "GET"
                },
                {
                    "signature": "api.example.com/v1/products",
                    "host": "api.example.com",
                    "path": "/v1/products",
                    "method": "GET"
                }
            ]
        }

        new_map = {
            "entries": [
                {
                    "signature": "api.example.com/v1/users",
                    "host": "api.example.com",
                    "path": "/v1/users",
                    "method": "GET"
                },
                {
                    "signature": "api.example.com/v1/orders",
                    "host": "api.example.com",
                    "path": "/v1/orders",
                    "method": "GET"
                }
            ]
        }

        comparison = compare_url_maps(old_map, new_map)
        self.assertIsInstance(comparison, dict)
        self.assertIn("added", comparison)
        self.assertIn("removed", comparison)
        self.assertIn("unchanged", comparison)

if __name__ == '__main__':
    unittest.main()