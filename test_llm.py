#!/usr/bin/env python3
"""
Test script for LLM integration in Auto APK Analyzer
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.llm_client import AppDiscoveryClient

def test_llm_integration():
    """Test LLM integration functionality."""
    print("Testing LLM Integration...")
    print("=" * 30)

    # Create app discovery client
    discovery_client = AppDiscoveryClient()

    # Show which services are configured
    print("Configured LLM Services:")
    for service_name, client in discovery_client.clients.items():
        status = "Configured" if client.is_configured else "Not configured"
        print(f"  {service_name}: {status}")

    # Test app discovery (only if at least one service is configured)
    any_configured = any(client.is_configured for client in discovery_client.clients.values())

    if any_configured:
        print("\nTesting app discovery...")
        query = "popular social media apps"
        results = discovery_client.discover_apps(query)

        for service, result in results.items():
            print(f"\n{service.upper()} Results:")
            if "Error" in result or "API key not configured" in result:
                print(f"  {result}")
            else:
                # Show first 200 characters of the result
                print(f"  {result[:200]}...")
    else:
        print("\nNo LLM services configured. Skipping app discovery test.")

if __name__ == "__main__":
    test_llm_integration()