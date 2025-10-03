# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This repository implements an automated APK analysis framework that runs on rooted test devices using an "ADB enumeration → static extraction → dynamic interception + Pinning bypass → component surface enumeration → normalized database storage" pipeline. The system automatically scans installed apps one by one, combining Frida/Reqable/Drozer to automatically aggregate URLs, methods, and parameters into a URL Map with replay and incremental comparison capabilities.

## Device Inventory and Baseline
The pipeline begins by enumerating installed applications on rooted devices using ADB package management commands:
- Uses `adb shell pm list packages -3` to list third-party packages
- Uses `adb shell pm list packages -f` to show APK paths
- Uses `adb shell pm path <package>` to get specific APK paths
- Pulls APKs locally using `adb pull` for static analysis and version fingerprinting

## Core Modules

### Static Extraction Subsystem
- Employs JADX to decompile APKs and extract hardcoded URLs, gateway paths, and third-party domains from strings, resources, and assets
- Uses APKLeaks for rapid URI/endpoint/secret scanning as static evidence supplementation
- Applies manual rules to filter noise (e.g., excluding irrelevant third-party telemetry)

### Dynamic Capture and Pinning Bypass
- Uses Reqable as MITM proxy to intercept real traffic with Python scripting engine for automatic annotation, filtering, and export of request elements
- Implements Frida for runtime hooking to bypass certificate pinning following OWASP MASTG multi-path Unpinning strategies
- Leverages Frida to inject interceptors or hook key methods in OkHttp/HttpURLConnection to record request/response metadata

### Automated App Behavior Triggering
- Uses Monkey to inject pseudo-random events driving broad UI coverage and active traffic generation
- Employs UIAutomator for deterministic replay of critical workflows in device-side independent processes
- Configures seed, throttling, and event distribution for reproducible experimental conditions

### Component Surface and Content URI Enumeration
- Uses Drozer to automatically enumerate exported components (activities/services/providers/receivers) to discover deep links, content providers, and reachable internal routes
- Validates content:// URI reachability and data structures through Drozer queries
- Supplements URL Map with component-based endpoints and risk annotations

### Flutter Application Handling
Special handling for Flutter applications which require additional steps due to their unique network stack:

#### Flutter Detection
- Checks for assets/flutter_assets directory in APK
- Looks for libflutter.so in native libraries (e.g., lib/arm64-v8a/)
- Identifies FlutterActivity or related Flutter engine configurations in Manifest

#### Why Standard MITM Fails
- Flutter's Dart network stack doesn't follow system proxy settings
- Uses its own certificate store, making system CA installation ineffective
- Requires both traffic routing and TLS certificate validation bypass

#### Interception Solutions
1. Repackaging approach (reFlutter):
   - Re-packages Flutter module with proxy settings and disabled TLS validation
   - Suitable for batch automation but requires signing for each version

2. Runtime Hooking (Frida):
   - Uses Frida scripts to disable TLS verification (e.g., NVISO's disable-flutter-tls-verification)
   - Hooks BoringSSL functions to bypass certificate validation
   - No re-signing required and compatible with multiple architectures

#### Traffic Routing
- Uses ProxyDroid/VPN/iptables/Wi-Fi hotspot to route traffic to proxy
- Combines with TLS bypass scripts for complete interception
- NVISO recommends this combination for reliable HTTPS traffic capture

### URL Map Normalization
- Unifies sources from static (JADX/APKLeaks), dynamic (Reqable/Frida), and component enumeration (Drozer) into standardized metadata:
  - Host, path, method, parameter patterns, authentication clues, evidence sources, and first discovery timestamps
- Normalizes path parameters with templating (e.g., /v1/users/{id}) while preserving example values, frequency, and last activity timestamps
- Supports sorting by activity and risk priority with incremental comparison capabilities

### Concurrency and Isolation Strategy
- Uses Reqable's "per-application traffic identification" to distinguish requests from concurrently scanned apps
- Prioritizes Frida-based in-app hooking for heavily pinned or special network stack applications
- Maintains isolated working directories and tagging systems per package

## Automation Pipeline Implementation

### Device Enumeration and APK Retrieval
```bash
# Enumerate and pull APKs
adb shell pm list packages -3 > packages.txt
for pkg in $(cut -d: -f2 packages.txt); do
  apk_path=$(adb shell pm path "$pkg" | sed 's/package://g')
  adb pull "$apk_path" ./workspace/$pkg/base.apk
done
```

### Static/Dynamic Orchestration and Merging
```python
# Pseudo-code for static/dynamic orchestration
for pkg in packages:
    # Detect if app is Flutter-based
    is_flutter = detect_flutter_app("./workspace/pkg/base.apk")

    static_hits = run_jadx_extract("./workspace/pkg/base.apk")
    static_hits |= run_apkleaks("./workspace/pkg/base.apk")

    if is_flutter:
        # Special handling for Flutter apps
        setup_flutter_interception(pkg)  # Route traffic + disable TLS
        frida_hook_flutter(pkg)          # Hook BoringSSL functions
    else:
        # Standard Android app handling
        start_reqable_capture(app=pkg)
        frida_hook_okhttp(pkg)

    drive_with_monkey(pkg, events=10000, seed=123)

    if not is_flutter:
        stop_reqable_capture()

    drozer_uris = drozer_enum_and_probe(pkg)
    url_map = normalize_merge(static_hits, reqable_flows, frida_logs, drozer_uris)
    save_url_map(pkg, url_map)
```

## Key Implementation Points
- ADB-based package management with `pm list packages`, `pm path`, and `adb pull` for discovery, sampling, and fingerprinting
- Reqable scripting for structured export with application attribution for concurrent scanning
- Frida-based OkHttp interception and method hooking for in-app URL/parameter capture
- Specialized Flutter handling with detection, traffic routing, and TLS bypass
- Drozer component discovery and content provider validation for comprehensive endpoint coverage
- Kiterunner and historical snapshot enumeration for route completion and version differentiation

## Extension and Replay Capabilities
- Combines Kiterunner with historical snapshots for gateway route enumeration and version gap completion
- Uses minimal request sets for replay validation of status codes and authentication requirements
- Implements UIAutomator test cases for deterministic replay and incremental difference detection

## Development Commands
```bash
# Initialize device connection and enumerate packages
adb devices
adb shell pm list packages -3

# Run static analysis on pulled APKs
python3 static_analyzer.py --input ./workspace/app/base.apk

# Start dynamic analysis with Reqable and Frida
python3 dynamic_analyzer.py --package com.example.app --duration 300

# Special handling for Flutter apps
python3 flutter_handler.py --package com.example.app --mode frida

# Enumerate components with Drozer
python3 component_scanner.py --package com.example.app

# Generate unified URL map
python3 url_mapper.py --static static.json --dynamic flows.json --components drozer.json

# Run Monkey for behavior triggering
adb shell monkey -p com.example.app -v 10000 -s 123 --throttle 200
```

## Cross-Platform Support
- Android: Full support through ADB, Frida, Reqable, and Drozer
- iOS: Requires jailbroken device with Frida-based SSL pinning bypass
- Flutter: Special handling for Android Flutter applications with dedicated detection and bypass

## Output Format
The URL Map includes:
- Endpoint signature (host+path+method)
- Parameter patterns and examples
- Authentication requirements
- Evidence traces linking back to discovery sources
- Activity timestamps and frequency data
- Component-based endpoint categorization
- Risk annotations and replay validation status
- Flutter-specific metadata when applicable