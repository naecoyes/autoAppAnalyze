#!/usr/bin/env python3
"""
Test script for Auto APK Analyzer components
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.device_manager import (
    is_device_connected,
    list_third_party_packages,
    get_apk_path,
    group_apps_by_developer
)

def test_device_manager():
    """Test device manager functionality."""
    print("Testing Device Manager...")
    print("=" * 30)

    # Test device connection
    connected = is_device_connected()
    print(f"Device connected: {connected}")

    if connected:
        # Test package listing
        print("\nListing third-party packages...")
        packages = list_third_party_packages()
        print(f"Found {len(packages)} packages")

        if packages:
            # Show first 5 packages
            print("Sample packages:")
            for pkg in packages[:5]:
                print(f"  {pkg}")

            # Test APK path retrieval for first package
            first_pkg = packages[0]
            print(f"\nGetting APK path for {first_pkg}...")
            apk_path = get_apk_path(first_pkg)
            print(f"APK Path: {apk_path}")

            # Test developer grouping
            print("\nGrouping apps by developer...")
            developer_groups = group_apps_by_developer(packages[:10])  # First 10 packages
            print(f"Grouped into {len(developer_groups)} developer groups:")
            for developer, app_list in list(developer_groups.items())[:3]:  # First 3 groups
                print(f"  {developer}: {len(app_list)} apps")
                for app in app_list[:2]:  # First 2 apps in each group
                    print(f"    {app}")

if __name__ == "__main__":
    test_device_manager()