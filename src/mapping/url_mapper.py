#!/usr/bin/env python3
"""
URL Mapping Module for Auto APK Analyzer
"""

import json
import time
from collections import defaultdict
from urllib.parse import urlparse

def create_url_mapping_entry(url, method='UNKNOWN', source='unknown', parameters=None):
    """
    Create a standardized URL mapping entry.

    Args:
        url (str): The URL
        method (str): HTTP method (GET, POST, etc.)
        source (str): Source of the URL (static, dynamic, component)
        parameters (list): List of parameters

    Returns:
        dict: URL mapping entry
    """
    parsed = urlparse(url)

    # Extract path parameters and normalize
    normalized_path = parsed.path
    path_params = []

    if parameters:
        path_params = parameters
        # Replace actual values with placeholders in the path
        for param in parameters:
            if param.get('type') == 'uuid':
                normalized_path = normalized_path.replace(param['value'], '{uuid}')
            elif param.get('type') == 'numeric_id':
                normalized_path = normalized_path.replace(param['value'], '{id}')
            elif param.get('type') == 'alphanumeric_id':
                normalized_path = normalized_path.replace(param['value'], '{param}')

    # Determine risk level
    risk_level = 'LOW'
    risk_indicators = [
        'admin', 'login', 'auth', 'token', 'password', 'secret',
        'key', 'config', 'debug', 'test', 'dev'
    ]

    for indicator in risk_indicators:
        if indicator in url.lower():
            risk_level = 'HIGH'
            break
        elif parameters and any(indicator in param.get('value', '').lower() for param in parameters):
            risk_level = 'MEDIUM'
            break

    return {
        'signature': f"{parsed.netloc}{normalized_path}",
        'host': parsed.netloc,
        'path': normalized_path,
        'method': method,
        'parameters': parameters or [],
        'sources': [source],
        'original_urls': [url],
        'risk_level': risk_level,
        'first_seen': time.time(),
        'last_seen': time.time(),
        'frequency': 1
    }

def merge_static_dynamic_data(static_results, dynamic_results, component_results=None):
    """
    Merge data from static, dynamic, and component analysis.

    Args:
        static_results (dict): Results from static analysis
        dynamic_results (list): Results from dynamic analysis
        component_results (dict): Results from component enumeration

    Returns:
        dict: Merged URL mapping
    """
    # Create a dictionary to hold merged entries
    merged_entries = {}

    # Process static analysis results
    if 'urls' in static_results:
        for entry in static_results['urls']:
            url_entry = create_url_mapping_entry(
                entry.get('url', ''),
                method='UNKNOWN',
                source='static',
                parameters=entry.get('parameters', [])
            )

            signature = url_entry['signature']
            if signature in merged_entries:
                # Merge with existing entry
                existing = merged_entries[signature]
                existing['sources'].extend(url_entry['sources'])
                existing['original_urls'].extend(url_entry['original_urls'])
                existing['parameters'].extend(url_entry['parameters'])
                existing['frequency'] += url_entry['frequency']
                existing['last_seen'] = max(existing['last_seen'], url_entry['last_seen'])

                # Update risk level if needed
                risk_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
                if risk_levels[url_entry['risk_level']] > risk_levels[existing['risk_level']]:
                    existing['risk_level'] = url_entry['risk_level']
            else:
                merged_entries[signature] = url_entry

    # Process dynamic analysis results
    for flow in dynamic_results:
        url = flow.get('url', '')
        method = flow.get('method', 'UNKNOWN')

        url_entry = create_url_mapping_entry(
            url,
            method=method,
            source='dynamic'
        )

        signature = url_entry['signature']
        if signature in merged_entries:
            # Merge with existing entry
            existing = merged_entries[signature]
            existing['sources'].extend(url_entry['sources'])
            existing['original_urls'].extend(url_entry['original_urls'])
            existing['method'] = method if method != 'UNKNOWN' else existing['method']
            existing['frequency'] += url_entry['frequency']
            existing['last_seen'] = max(existing['last_seen'], url_entry['last_seen'])
        else:
            merged_entries[signature] = url_entry

    # Process component enumeration results
    if component_results and 'providers' in component_results:
        for provider in component_results['providers']:
            if provider.get('accessible', False):
                uri = provider.get('uri', '')
                if uri:
                    url_entry = create_url_mapping_entry(
                        f"content://{uri}",
                        method='CONTENT_PROVIDER',
                        source='component'
                    )

                    signature = url_entry['signature']
                    if signature in merged_entries:
                        # Merge with existing entry
                        existing = merged_entries[signature]
                        existing['sources'].extend(url_entry['sources'])
                        existing['original_urls'].extend(url_entry['original_urls'])
                        existing['method'] = 'CONTENT_PROVIDER'
                        existing['frequency'] += url_entry['frequency']
                        existing['last_seen'] = max(existing['last_seen'], url_entry['last_seen'])
                    else:
                        merged_entries[signature] = url_entry

    # Remove duplicates from sources and original_urls
    for entry in merged_entries.values():
        entry['sources'] = list(set(entry['sources']))
        entry['original_urls'] = list(set(entry['original_urls']))

    return {
        'entries': list(merged_entries.values()),
        'domains': static_results.get('domains', []),
        'endpoints': static_results.get('endpoints', []),
        'secrets': static_results.get('secrets', []),
        'permissions': static_results.get('permissions', []),
        'certificates': static_results.get('certificates', []),
        'timestamp': time.time()
    }

def generate_url_map(static_results, dynamic_results, component_results=None):
    """
    Generate a comprehensive URL map from all analysis results.

    Args:
        static_results (dict): Results from static analysis
        dynamic_results (list): Results from dynamic analysis
        component_results (dict): Results from component enumeration

    Returns:
        dict: Comprehensive URL map
    """
    # Merge all data sources
    merged_data = merge_static_dynamic_data(static_results, dynamic_results, component_results)

    # Generate summary statistics
    total_entries = len(merged_data['entries'])
    risk_distribution = defaultdict(int)
    source_distribution = defaultdict(int)
    method_distribution = defaultdict(int)

    for entry in merged_data['entries']:
        risk_distribution[entry['risk_level']] += 1
        method_distribution[entry['method']] += 1
        for source in entry['sources']:
            source_distribution[source] += 1

    # Create comprehensive URL map
    url_map = {
        'metadata': {
            'generated_at': time.time(),
            'total_entries': total_entries,
            'risk_distribution': dict(risk_distribution),
            'source_distribution': dict(source_distribution),
            'method_distribution': dict(method_distribution)
        },
        'entries': merged_data['entries'],
        'domains': merged_data['domains'],
        'endpoints': merged_data['endpoints'],
        'secrets': merged_data['secrets'],
        'permissions': merged_data['permissions'],
        'certificates': merged_data['certificates']
    }

    return url_map

def save_url_map(url_map, output_path):
    """
    Save URL map to a JSON file.

    Args:
        url_map (dict): URL map to save
        output_path (str): Path to save the file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(url_map, f, indent=2)
        print(f"URL map saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving URL map: {e}")
        return False

def load_url_map(input_path):
    """
    Load URL map from a JSON file.

    Args:
        input_path (str): Path to the file

    Returns:
        dict: Loaded URL map, or None if failed
    """
    try:
        with open(input_path, 'r') as f:
            url_map = json.load(f)
        print(f"URL map loaded from {input_path}")
        return url_map
    except Exception as e:
        print(f"Error loading URL map: {e}")
        return None

def compare_url_maps(old_map, new_map):
    """
    Compare two URL maps to identify changes.

    Args:
        old_map (dict): Old URL map
        new_map (dict): New URL map

    Returns:
        dict: Comparison results
    """
    old_signatures = {entry['signature'] for entry in old_map.get('entries', [])}
    new_signatures = {entry['signature'] for entry in new_map.get('entries', [])}

    added = new_signatures - old_signatures
    removed = old_signatures - new_signatures
    unchanged = old_signatures & new_signatures

    return {
        'added': list(added),
        'removed': list(removed),
        'unchanged': list(unchanged),
        'summary': {
            'added_count': len(added),
            'removed_count': len(removed),
            'unchanged_count': len(unchanged)
        }
    }

# Example usage
if __name__ == "__main__":
    # Sample data for testing
    static_results = {
        "urls": [
            {
                "url": "https://api.example.com/v1/users/123",
                "original_url": "https://api.example.com/v1/users/123",
                "parameters": [{"type": "numeric_id", "value": "123"}],
                "sources": ["jadx"]
            },
            {
                "url": "https://api.example.com/v1/products",
                "original_url": "https://api.example.com/v1/products",
                "parameters": [],
                "sources": ["jadx"]
            }
        ],
        "domains": ["api.example.com"],
        "endpoints": ["/api/v1/login"],
        "secrets": ["API_KEY=abc123"],
        "permissions": ["android.permission.INTERNET"]
    }

    dynamic_results = [
        {
            "method": "GET",
            "url": "https://api.example.com/v1/users/456",
            "headers": {"Authorization": "Bearer token"},
            "response_status": 200
        },
        {
            "method": "POST",
            "url": "https://api.example.com/v1/login",
            "headers": {"Content-Type": "application/json"},
            "response_status": 401
        }
    ]

    component_results = {
        "providers": [
            {
                "uri": "com.example.app.data.provider",
                "accessible": True
            }
        ]
    }

    # Generate URL map
    url_map = generate_url_map(static_results, dynamic_results, component_results)
    print("Generated URL Map:")
    print(json.dumps(url_map, indent=2))

    # Save URL map
    # save_url_map(url_map, "url_map.json")

    # Compare URL maps
    # comparison = compare_url_maps(url_map, url_map)
    # print("Comparison Results:")
    # print(json.dumps(comparison, indent=2))