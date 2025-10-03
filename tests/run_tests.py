#!/usr/bin/env python3
"""
Test runner for Auto APK Analyzer
"""

import unittest
import sys
import os

def run_all_tests():
    """Run all tests in the tests directory"""
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    sys.path.append(src_path)

    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests())