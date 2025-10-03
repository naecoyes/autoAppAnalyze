#!/usr/bin/env python3
"""
Demo script for Auto APK Analyzer
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def demo_overview():
    """Print an overview of the Auto APK Analyzer functionality."""
    print("Auto APK Analyzer Demo")
    print("=" * 50)
    print()

    print("This tool provides several key capabilities for mobile app security analysis:")
    print()

    print("1. Device Analysis Mode:")
    print("   - Enumerates all third-party apps on a connected Android device")
    print("   - Groups apps by developer for systematic analysis")
    print("   - Pulls APKs and organizes them in a structured workspace")
    print("   Usage: python3 src/main.py --mode device")
    print()

    print("2. LLM-Based App Discovery:")
    print("   - Leverages AI models (Perplexity, Gemini, ChatGPT, ModelScope, OpenRouter) to discover relevant apps")
    print("   - Identifies potential APIs and endpoints for security analysis")
    print("   - Provides structured information about app functionality and security considerations")
    print("   Usage: python3 src/main.py --mode llm --query \"mobile banking apps in Southeast Asia\"")
    print()

    print("3. Predefined Analysis Flows:")
    print("   - Structured workflows for different analysis scenarios")
    print("   - Task and subtask management with progress tracking")
    print("   - Support for complex multi-stage analysis pipelines")
    print("   Usage: python3 src/main.py --flow device_analysis")
    print("   Available flows: device_analysis, file_analysis, llm_discovery, full_analysis")
    print()

    print("4. Static Analysis (Planned):")
    print("   - Extracts URLs, endpoints, and secrets from APK files")
    print("   - Uses JADX and APKLeaks for comprehensive static analysis")
    print("   - Integrates with MobSF for automated scanning")
    print()

    print("5. Dynamic Analysis (Planned):")
    print("   - Captures real API traffic using Reqable proxy")
    print("   - Bypasses certificate pinning with Frida scripts")
    print("   - Special handling for Flutter applications")
    print()

    print("6. Component Enumeration (Planned):")
    print("   - Discovers exported components using Drozer")
    print("   - Validates content:// URIs and deep links")
    print()

    print("To get started:")
    print("1. Connect an Android device with USB debugging enabled")
    print("2. Run: python3 src/main.py --mode device")
    print()
    print("To use LLM features:")
    print("1. Configure API keys in api_keys.json")
    print("2. Run: python3 src/main.py --mode llm --query \"popular social media apps\"")
    print()
    print("To execute a predefined flow:")
    print("1. Run: python3 src/main.py --flow device_analysis")

if __name__ == "__main__":
    demo_overview()