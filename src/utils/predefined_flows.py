#!/usr/bin/env python3
"""
Predefined Flows, Tasks, and Subtasks for Auto APK Analyzer
"""

from typing import List, Dict
from .task_manager import TaskPriority

# Predefined flows for APK analysis
PREDEFINED_FLOWS = [
    {
        "flow_id": "device_analysis",
        "name": "Device APK Analysis",
        "description": "Complete analysis of APKs on connected Android device"
    },
    {
        "flow_id": "file_analysis",
        "name": "File-based APK Analysis",
        "description": "Analysis of APK files provided as input"
    },
    {
        "flow_id": "llm_discovery",
        "name": "LLM-based App Discovery",
        "description": "Discovery of mobile apps and APIs using LLM services"
    },
    {
        "flow_id": "full_analysis",
        "name": "Complete APK Analysis",
        "description": "Full static, dynamic, and AI-assisted analysis pipeline"
    }
]

# Predefined tasks for each flow
PREDEFINED_TASKS = {
    "device_analysis": [
        {
            "task_id": "device_connectivity",
            "name": "Device Connectivity Check",
            "description": "Verify Android device is connected and accessible via ADB",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "package_enumeration",
            "name": "Package Enumeration",
            "description": "List all third-party packages on the device",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "developer_grouping",
            "name": "Developer-based Grouping",
            "description": "Group apps by developer for organized analysis",
            "priority": TaskPriority.MEDIUM
        },
        {
            "task_id": "apk_extraction",
            "name": "APK Extraction",
            "description": "Pull APK files from device to local workspace",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "workspace_organization",
            "name": "Workspace Organization",
            "description": "Organize extracted APKs in developer-based workspaces",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "file_analysis": [
        {
            "task_id": "file_validation",
            "name": "APK File Validation",
            "description": "Validate input APK files exist and are readable",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "static_analysis",
            "name": "Static Analysis",
            "description": "Perform static analysis on APK files using JADX and APKLeaks",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "url_extraction",
            "name": "URL and Endpoint Extraction",
            "description": "Extract URLs, endpoints, and secrets from static analysis results",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "metadata_analysis",
            "name": "Metadata Analysis",
            "description": "Analyze APK metadata for security insights",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "llm_discovery": [
        {
            "task_id": "api_key_validation",
            "name": "API Key Validation",
            "description": "Verify LLM API keys are configured and valid",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "app_discovery",
            "name": "App Discovery",
            "description": "Discover relevant mobile apps based on query",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "api_analysis",
            "name": "API Analysis",
            "description": "Analyze potential APIs and endpoints for discovered apps",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "security_assessment",
            "name": "Security Assessment",
            "description": "Identify potential security considerations for apps and APIs",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "full_analysis": [
        {
            "task_id": "preparation",
            "name": "Analysis Preparation",
            "description": "Prepare environment and validate prerequisites",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "static_phase",
            "name": "Static Analysis Phase",
            "description": "Complete static analysis of APK files",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "dynamic_phase",
            "name": "Dynamic Analysis Phase",
            "description": "Dynamic traffic capture and analysis",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "component_phase",
            "name": "Component Enumeration Phase",
            "description": "Enumeration of exported components and content URIs",
            "priority": TaskPriority.MEDIUM
        },
        {
            "task_id": "llm_phase",
            "name": "LLM Analysis Phase",
            "description": "AI-assisted analysis using LLM services",
            "priority": TaskPriority.MEDIUM
        },
        {
            "task_id": "consolidation",
            "name": "Results Consolidation",
            "description": "Combine all analysis results into unified URL Map",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "reporting",
            "name": "Report Generation",
            "description": "Generate comprehensive analysis reports",
            "priority": TaskPriority.MEDIUM
        }
    ]
}

# Predefined subtasks for complex tasks
PREDEFINED_SUBTASKS = {
    "package_enumeration": [
        {
            "task_id": "adb_connect",
            "name": "ADB Connection",
            "description": "Establish ADB connection to device",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "package_list",
            "name": "List Packages",
            "description": "Execute 'adb shell pm list packages -3' command",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "package_filter",
            "name": "Filter Packages",
            "description": "Filter out system packages and keep only third-party apps",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "developer_grouping": [
        {
            "task_id": "package_metadata",
            "name": "Extract Package Metadata",
            "description": "Extract metadata for each package to identify developers",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "developer_identification",
            "name": "Developer Identification",
            "description": "Identify developers based on package name patterns",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "group_creation",
            "name": "Create Developer Groups",
            "description": "Create groups of apps organized by developer",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "apk_extraction": [
        {
            "task_id": "apk_path_discovery",
            "name": "APK Path Discovery",
            "description": "Discover APK file paths on device for each package",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "apk_pull",
            "name": "APK Pull Operations",
            "description": "Pull APK files from device using 'adb pull'",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "file_validation",
            "name": "Pulled File Validation",
            "description": "Validate pulled APK files are complete and readable",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "static_analysis": [
        {
            "task_id": "jadx_analysis",
            "name": "JADX Decompilation",
            "description": "Decompile APK using JADX for code analysis",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "apkleaks_scan",
            "name": "APKLeaks Scan",
            "description": "Scan APK for URLs, endpoints, and secrets using APKLeaks",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "mobsf_scan",
            "name": "MobSF Analysis",
            "description": "Perform comprehensive analysis using MobSF",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "dynamic_phase": [
        {
            "task_id": "proxy_setup",
            "name": "Proxy Setup",
            "description": "Configure and start HTTP proxy for traffic capture",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "pinning_bypass",
            "name": "Certificate Pinning Bypass",
            "description": "Implement certificate pinning bypass using Frida",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "traffic_capture",
            "name": "Traffic Capture",
            "description": "Capture and record HTTP/S traffic from apps",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "flutter_handling",
            "name": "Flutter App Handling",
            "description": "Special handling for Flutter applications",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "component_phase": [
        {
            "task_id": "drozer_setup",
            "name": "Drozer Setup",
            "description": "Configure and start Drozer for component analysis",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "component_enumeration",
            "name": "Component Enumeration",
            "description": "Enumerate exported activities, services, providers, and receivers",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "content_uri_probe",
            "name": "Content URI Probing",
            "description": "Probe and validate content:// URIs",
            "priority": TaskPriority.MEDIUM
        }
    ],
    "llm_phase": [
        {
            "task_id": "service_initialization",
            "name": "LLM Service Initialization",
            "description": "Initialize connections to configured LLM services",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "app_analysis",
            "name": "App Analysis Queries",
            "description": "Query LLMs for app behavior and API insights",
            "priority": TaskPriority.HIGH
        },
        {
            "task_id": "endpoint_enrichment",
            "name": "Endpoint Enrichment",
            "description": "Use LLMs to enrich discovered endpoints with context",
            "priority": TaskPriority.MEDIUM
        }
    ]
}

def get_flow_definition(flow_id: str) -> Dict:
    """Get the definition for a specific flow."""
    for flow in PREDEFINED_FLOWS:
        if flow["flow_id"] == flow_id:
            return flow
    return None

def get_tasks_for_flow(flow_id: str) -> List[Dict]:
    """Get predefined tasks for a specific flow."""
    return PREDEFINED_TASKS.get(flow_id, [])

def get_subtasks_for_task(task_id: str) -> List[Dict]:
    """Get predefined subtasks for a specific task."""
    return PREDEFINED_SUBTASKS.get(task_id, [])