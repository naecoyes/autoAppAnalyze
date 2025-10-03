# TODO List for Auto APK Analyzer

## Core Module Implementation

### Static Analysis Modules
- [ ] Implement JADX integration for APK decompilation
- [ ] Implement APKLeaks integration for URI/endpoint/secret scanning
- [ ] Implement MobSF REST API client for automated scanning
- [ ] Create static URL extraction and normalization functions

### Dynamic Analysis Modules
- [ ] Implement Reqable proxy integration with scripting engine
- [ ] Implement Frida-based certificate pinning bypass for standard Android apps
- [ ] Implement Frida-based TLS bypass for Flutter applications
- [ ] Create traffic capture and export functionality

### Component Enumeration Modules
- [ ] Implement Drozer integration for component discovery
- [ ] Create content:// URI validation and probing functions
- [ ] Implement exported component enumeration

### Device Management
- [x] Implement ADB package enumeration functionality
- [x] Create APK pulling and workspace management
- [x] Implement device connection validation
- [x] Add developer grouping functionality

## Flutter-Specific Implementation
- [ ] Create Flutter app detection module (check for flutter_assets, libflutter.so, FlutterActivity)
- [ ] Implement traffic routing setup (ProxyDroid/VPN/iptables integration)
- [ ] Integrate NVISO's disable-flutter-tls-verification Frida scripts
- [ ] Create reFlutter repackaging workflow (optional)

## Automation Pipeline
- [ ] Implement main orchestration pipeline
- [ ] Create Monkey-based app behavior triggering
- [ ] Implement UIAutomator integration for deterministic testing
- [ ] Develop concurrent scanning with proper isolation

## URL Map Generation
- [ ] Implement URL normalization and deduplication
- [ ] Create path parameter templating (e.g., /v1/users/{id})
- [ ] Implement evidence source tracking and metadata storage
- [ ] Create JSON/SQLite export functionality

## Extension Features
- [ ] Integrate Kiterunner for active enumeration
- [ ] Implement historical snapshot integration (Wayback Machine/crt.sh)
- [ ] Create replay validation capabilities
- [ ] Implement incremental comparison functionality

## API Integration
- [x] Integrate Perplexity API for enhanced analysis
- [x] Integrate Gemini API for app and API discovery
- [x] Integrate ChatGPT API for app and API discovery
- [x] Integrate ModelScope API for app and API discovery
- [x] Integrate OpenRouter API for app and API discovery
- [ ] Configure subfinder with API keys for domain enumeration:
  - [ ] bevigil
  - [ ] binaryedge
  - [ ] bufferover
  - [ ] c99
  - [ ] certspotter
  - [ ] chaos
  - [ ] fofa
  - [ ] quake
  - [ ] securitytrails
  - [ ] virustotal
  - [ ] whoisxmlapi
  - [ ] zoomeyeapi

## Workflow Management
- [x] Implement task management system with flows, tasks, and subtasks
- [x] Create predefined flows for common analysis scenarios
- [x] Implement task priority and status tracking
- [ ] Add task execution logic for predefined flows
- [ ] Implement progress reporting and metrics
- [ ] Add task dependency management

## Integration and Reporting
- [ ] Create integration APIs for asset management platforms (ARL/ScopeSentry)
- [ ] Implement reporting and visualization components
- [ ] Create OpenAPI specification generation
- [ ] Develop test case skeleton generation

## Testing and Documentation
- [ ] Create unit tests for core modules
- [ ] Implement integration tests for the full pipeline
- [ ] Write comprehensive documentation
- [ ] Create example configurations and usage guides

## Priority Implementation Order

### Phase 1: Foundation (High Priority)
1. [x] Device management and ADB integration
2. [x] LLM integration for app discovery
3. [x] Workflow management system
4. [ ] Static analysis modules (JADX, APKLeaks)
5. [ ] Basic URL normalization and deduplication
6. [ ] Core orchestration pipeline

### Phase 2: Dynamic Analysis (Medium Priority)
1. [ ] Reqable proxy integration
2. [ ] Frida-based certificate pinning bypass
3. [ ] Traffic capture and export functionality
4. [ ] Monkey-based behavior triggering

### Phase 3: Advanced Features (Low Priority)
1. [ ] Flutter app detection and handling
2. [ ] Drozer component enumeration
3. [ ] Kiterunner integration
4. [ ] Historical snapshot integration