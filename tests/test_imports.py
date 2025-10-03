#!/usr/bin/env python3
"""
Test script to verify all modules can be imported successfully
"""

import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.append(src_path)

def test_imports():
    """Test that all modules can be imported without errors"""
    modules_to_test = [
        # Utils modules
        'utils.device_manager',
        'utils.workspace_manager',
        'utils.llm_client',
        'utils.task_manager',
        'utils.predefined_flows',
        'utils.url_normalizer',

        # Analysis modules
        'static.static_analyzer',
        'dynamic.dynamic_analyzer',
        'component.component_enumerator',
        'flutter.flutter_handler',
        'mapping.url_mapper',

        # Main module
        'main'
    ]

    failed_imports = []

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            failed_imports.append((module, str(e)))
            print(f"✗ {module}: {e}")

    if failed_imports:
        print("\nFailed imports:")
        for module, error in failed_imports:
            print(f"  {module}: {error}")
        return False
    else:
        print("\nAll modules imported successfully!")
        return True

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)