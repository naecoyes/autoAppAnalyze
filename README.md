# Auto APK Analyzer

An automated APK analysis framework that discovers hidden mobile APIs through static extraction, dynamic interception, and enumeration completion techniques.

## Overview

This tool implements a comprehensive pipeline for analyzing Android applications (APKs) to discover APIs that are difficult to detect through traditional scanning methods. The system works on rooted test devices and combines multiple analysis techniques:

1. **Static Analysis**: Extracts URLs, endpoints, and secrets from APK files using JADX, APKLeaks, and MobSF
2. **Dynamic Interception**: Captures real API traffic using proxy tools with Frida-based certificate pinning bypass
3. **Component Enumeration**: Discovers exported components and content URIs using Drozer
4. **Active Enumeration**: Completes API coverage using advanced techniques
5. **AI-Assisted Discovery**: Leverages LLMs (Gemini, ChatGPT, Perplexity, ModelScope, OpenRouter) for enhanced app and API discovery
6. **Structured Workflows**: Predefined flows with task and subtask management for systematic analysis

## Key Features

- Automated scanning of installed applications on rooted Android devices
- Special handling for Flutter applications with dedicated detection and interception
- Three-layer analysis approach: static extraction → dynamic interception → enumeration completion
- URL Map generation with normalized endpoint information
- Support for certificate pinning bypass using Frida scripts
- Developer-based APK organization for systematic analysis
- Integration with asset management platforms
- AI-assisted discovery using multiple LLMs (Gemini, ChatGPT, Perplexity, ModelScope, OpenRouter)
- Structured workflow management with predefined flows, tasks, and subtasks
- Complete testing framework with unit and integration tests

## Prerequisites

- Rooted Android device or emulator
- ADB (Android Debug Bridge)
- Python 3.x
- Required tools: JADX, APKLeaks, Reqable, Frida, Drozer, MobSF
  - JADX: Installed via Homebrew or manually
  - APKLeaks: Installed via Homebrew
  - MobSF: Installed via pip
  - Frida: Installed via pip
  - Drozer: Installed via pip
  - Reqable: Needs to be installed separately
- For Flutter apps: Specialized Frida scripts for TLS bypass
- API keys for LLM services (optional but recommended)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd auto-apk-analyze

# Install Python dependencies
pip install -r requirements.txt

# Install additional tools
brew install jadx apkleaks
pip install mobsf drozer frida-tools

# Install Frida server on your Android device
# Download from: https://github.com/frida/frida/releases
```

## Configuration

1. Configure API keys in `api_keys.json` for LLM services and domain enumeration tools
2. Update paths in `config.json` for MCP servers and tools if needed

## Usage

### Device Analysis Mode (Default)
```bash
# Analyze all third-party apps on connected device and organize by developer
python3 src/main.py --mode device
```

### LLM Discovery Mode
```bash
# Discover apps and APIs using LLM services
python3 src/main.py --mode llm --query "mobile banking apps in Southeast Asia"
```

### Predefined Flow Execution
```bash
# Execute a predefined analysis flow
python3 src/main.py --flow device_analysis

# Available flows:
# - device_analysis: Complete analysis of APKs on connected Android device
# - file_analysis: Analysis of APK files provided as input
# - llm_discovery: Discovery of mobile apps and APIs using LLM services
# - full_analysis: Full static, dynamic, and AI-assisted analysis pipeline
```

### Static Analysis Mode
```bash
# Analyze a specific APK file
python3 src/main.py --input /path/to/app.apk --mode static
```

### Full Analysis Mode
```bash
# Perform complete analysis (static + dynamic)
python3 src/main.py --input /path/to/app.apk --mode full
```

## Architecture

The pipeline consists of several main modules:

1. **Device Management**: Enumerates apps on device and organizes them by developer
2. **Static Extraction Subsystem**: Uses JADX, APKLeaks, and MobSF to extract hardcoded URLs, endpoints, and secrets
3. **Dynamic Capture Module**: Employs Reqable proxy with Frida hooks for traffic interception and certificate pinning bypass
4. **Component Enumeration Module**: Uses Drozer to discover exported components and content URIs
5. **Flutter App Handler**: Specialized module for detecting and handling Flutter applications
6. **URL Mapping System**: Consolidates findings from all sources into a normalized URL Map
7. **AI-Assisted Discovery**: Integrates with LLMs for enhanced app and API discovery
8. **Task Management**: Structured workflows with task and subtask management
9. **Workspace Management**: Organizes analysis results by developer and app

## Special Flutter App Handling

The framework includes specialized handling for Flutter applications which use a different network stack:

- Detection of Flutter apps through assets/flutter_assets directory and libflutter.so
- Traffic routing via ProxyDroid/VPN/iptables
- TLS certificate validation bypass using Frida scripts
- Two approaches: reFlutter repackaging or runtime hooking
- Dedicated Frida scripts for BoringSSL function hooking
- Automatic configuration of proxy settings for Flutter apps

## Output

The analysis generates a comprehensive URL Map including:
- Endpoint signatures (host+path+method)
- Parameter patterns and examples
- Authentication requirements
- Evidence traces and discovery sources
- Activity timestamps and frequency data
- Risk annotations and validation status
- Developer-based organization for systematic analysis
- Component-based endpoint categorization
- Flutter-specific metadata when applicable
- Normalized path parameters with templating (e.g., /v1/users/{id})
- Support for sorting by activity and risk priority
- Incremental comparison capabilities for version differentiation

## LLM Integration

The tool can leverage multiple LLMs for enhanced discovery:
- **Perplexity**: For real-time information retrieval about apps and APIs
- **Gemini**: For advanced analysis and pattern recognition
- **ChatGPT**: For comprehensive app behavior understanding
- **ModelScope**: For access to Qwen models and other Chinese LLMs
- **OpenRouter**: For access to multiple models through a single API

API keys should be configured in `api_keys.json` to enable these features.

## Workflow Management

The tool includes a comprehensive task management system with:

### Predefined Flows
1. **Device Analysis Flow**: Complete analysis of APKs on connected Android device
2. **File Analysis Flow**: Analysis of APK files provided as input
3. **LLM Discovery Flow**: Discovery of mobile apps and APIs using LLM services
4. **Full Analysis Flow**: Complete static, dynamic, and AI-assisted analysis pipeline

### Task Hierarchy
Each flow contains multiple tasks, and complex tasks can have subtasks:
- Tasks have priorities (Low, Medium, High, Critical)
- Tasks can be in states (Pending, In Progress, Completed, Failed)
- Parent tasks automatically complete when all subtasks are completed
- Progress tracking and status reporting

### Example Task Structure
```
Device Analysis Flow
├── Device Connectivity Check
├── Package Enumeration
│   ├── ADB Connection
│   ├── List Packages
│   └── Filter Packages
├── Developer-based Grouping
│   ├── Extract Package Metadata
│   ├── Developer Identification
│   └── Create Developer Groups
├── APK Extraction
│   ├── APK Path Discovery
│   ├── APK Pull Operations
│   └── Pulled File Validation
└── Workspace Organization
```