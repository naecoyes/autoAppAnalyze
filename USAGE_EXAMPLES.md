# Auto APK Analyzer - Usage Examples

This document provides practical examples of how to use the Auto APK Analyzer tool.

## 1. Device Analysis Mode (Default)

Analyze all third-party apps on a connected Android device and organize results by developer:

```bash
python3 src/main.py
```

Or explicitly specify the mode:

```bash
python3 src/main.py --mode device
```

This will:
1. Connect to the Android device via ADB
2. List all third-party packages
3. Group apps by developer
4. Pull APKs to local workspace
5. Perform static analysis on each APK
6. Generate URL maps and save results

## 2. Analyzing a Single APK File

Analyze a specific APK file:

```bash
python3 src/main.py --input /path/to/app.apk
```

## 3. Analyzing Multiple APK Files

Analyze all APK files in a directory:

```bash
python3 src/main.py --input /path/to/apk/directory
```

## 4. Static Analysis Only

Perform only static analysis (no dynamic interception):

```bash
python3 src/main.py --input /path/to/app.apk --mode static
```

## 5. LLM Discovery Mode

Use LLM services to discover relevant apps and APIs:

```bash
python3 src/main.py --mode llm --query "mobile banking apps in Southeast Asia"
```

Note: Requires API keys configured in `api_keys.json`.

## 6. Predefined Flow Execution

Execute a predefined analysis flow:

```bash
# Device analysis flow
python3 src/main.py --flow device_analysis

# File analysis flow
python3 src/main.py --flow file_analysis --input /path/to/apk

# LLM discovery flow
python3 src/main.py --flow llm_discovery --query "fintech apps"

# Full analysis flow
python3 src/main.py --flow full_analysis --input /path/to/app.apk
```

## 7. Custom Output Directory

Specify a custom output directory for results:

```bash
python3 src/main.py --input /path/to/app.apk --output /path/to/results
```

## 8. Configuration Files

### config.json
Configure tool paths and MCP servers:

```json
{
  "mcp_servers": {
    "mobile_app_testing": {
      "command": "node",
      "args": ["/path/to/mobile-app-testing-mcp/dist/index.js"]
    },
    "jadx_mcp_server": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "--directory",
        "/path/to/jadx-mcp-server",
        "run",
        "jadx_mcp_server.py"
      ]
    }
  },
  "tools": {
    "adb": "/usr/local/bin/adb",
    "frida": "/usr/local/bin/frida",
    "jadx": "/path/to/jadx/bin/jadx",
    "apkleaks": "/usr/local/bin/apkleaks",
    "mobsf": "/usr/local/bin/mobsf",
    "drozer": "/usr/local/bin/drozer"
  }
}
```

### api_keys.json
Configure API keys for LLM services:

```json
{
  "perplexity": "your_perplexity_api_key",
  "gemini": "your_gemini_api_key",
  "chatgpt": "your_chatgpt_api_key",
  "modelscope": "your_modelscope_api_key",
  "openrouter": "your_openrouter_api_key"
}
```

## 9. Workspace Structure

The tool creates a structured workspace for organizing analysis results:

```
workspace/
├── apks/
│   ├── google/
│   │   ├── com.google.android.apps.photos.apk
│   │   └── com.google.android.apps.photos_results/
│   │       ├── static_results.json
│   │       ├── url_map.json
│   │       └── jadx_output/
│   └── facebook/
│       ├── com.facebook.katana.apk
│       └── com.facebook.katana_results/
├── results/
│   ├── google/
│   │   └── com.google.android.apps.photos_results.json
│   └── facebook/
│       └── com.facebook.katana_results.json
└── logs/
```

## 10. URL Map Output Format

The URL map is generated in JSON format with the following structure:

```json
{
  "metadata": {
    "generated_at": 1234567890.123,
    "total_entries": 42,
    "risk_distribution": {
      "LOW": 25,
      "MEDIUM": 12,
      "HIGH": 5
    }
  },
  "entries": [
    {
      "signature": "api.example.com/v1/users/{id}",
      "host": "api.example.com",
      "path": "/v1/users/{id}",
      "method": "GET",
      "parameters": [
        {
          "type": "numeric_id",
          "value": "123"
        }
      ],
      "sources": ["static", "dynamic"],
      "original_urls": [
        "https://api.example.com/v1/users/123",
        "https://api.example.com/v1/users/456"
      ],
      "risk_level": "MEDIUM",
      "first_seen": 1234567890.123,
      "last_seen": 1234567890.123,
      "frequency": 2
    }
  ],
  "domains": ["api.example.com", "cdn.example.com"],
  "endpoints": ["/api/v1/login", "/api/v1/register"]
}
```

## 11. Running Tests

Run all unit tests:

```bash
python3 tests/run_tests.py
```

Run specific test modules:

```bash
python3 -m unittest tests.test_static_analyzer
python3 -m unittest tests.test_dynamic_analyzer
python3 -m unittest tests.test_component_enumerator
```

## 12. Troubleshooting

### Common Issues

1. **ADB Connection Failed**
   - Ensure device is connected: `adb devices`
   - Enable USB debugging on device
   - Accept debugging authorization on device

2. **Frida Not Working**
   - Ensure Frida server is running on device
   - Check Frida version compatibility
   - Verify device is rooted

3. **Drozer Not Working**
   - Ensure Drozer agent is installed on device
   - Start Drozer server: `drozer server start`

4. **Tool Not Found**
   - Update paths in `config.json`
   - Install missing tools via package manager

### Debugging Tips

1. Run with verbose output to see detailed logs
2. Check workspace/logs/ for detailed error logs
3. Use `--mode static` for troubleshooting dynamic analysis issues
4. Test individual modules separately to isolate problems