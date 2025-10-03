#!/usr/bin/env python3
"""
URL Normalization and Standardization Module for Auto APK Analyzer
"""

import re
import json
from urllib.parse import urlparse, urlunparse
from collections import defaultdict

def normalize_url(url):
    """
    Normalize a URL by standardizing its format.

    Args:
        url (str): URL to normalize

    Returns:
        str: Normalized URL
    """
    try:
        # Parse the URL
        parsed = urlparse(url)

        # Normalize scheme (lowercase)
        scheme = parsed.scheme.lower() if parsed.scheme else ''

        # Normalize netloc (lowercase, remove trailing dots)
        netloc = parsed.netloc.lower().rstrip('.') if parsed.netloc else ''

        # Normalize path (remove trailing slash for non-root paths)
        path = parsed.path
        if path and path != '/':
            path = path.rstrip('/')

        # Normalize query and fragment (keep as-is for now)
        query = parsed.query
        fragment = parsed.fragment

        # Reconstruct the URL
        normalized = urlunparse((scheme, netloc, path, parsed.params, query, fragment))
        return normalized

    except Exception as e:
        print(f"Error normalizing URL {url}: {e}")
        return url

def extract_path_parameters(url):
    """
    Extract path parameters from a URL and replace them with placeholders.

    Args:
        url (str): URL to process

    Returns:
        tuple: (normalized_url, parameters)
    """
    try:
        parsed = urlparse(url)
        path = parsed.path

        # Common patterns for path parameters
        # UUIDs
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        # Numeric IDs
        numeric_pattern = r'/\d+/'
        # Alphanumeric IDs
        alphanumeric_pattern = r'/[a-zA-Z0-9]+/'

        parameters = []

        # Extract UUIDs
        uuid_matches = re.findall(uuid_pattern, path)
        for match in uuid_matches:
            parameters.append({'type': 'uuid', 'value': match})
            path = path.replace(match, '{uuid}')

        # Extract numeric IDs
        numeric_matches = re.findall(numeric_pattern, path)
        for match in numeric_matches:
            param_value = match.strip('/')
            parameters.append({'type': 'numeric_id', 'value': param_value})
            path = path.replace(match, '/{id}/')

        # Extract alphanumeric IDs (more generic)
        alphanumeric_matches = re.findall(alphanumeric_pattern, path)
        for match in alphanumeric_matches:
            param_value = match.strip('/')
            # Skip common words that are unlikely to be parameters
            if param_value.lower() not in ['api', 'v1', 'v2', 'v3', 'users', 'user', 'products', 'product']:
                parameters.append({'type': 'alphanumeric_id', 'value': param_value})
                path = path.replace(f'/{param_value}/', '/{param}/')

        # Reconstruct URL with normalized path
        normalized_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))

        return normalized_url, parameters

    except Exception as e:
        print(f"Error extracting path parameters from URL {url}: {e}")
        return url, []

def deduplicate_urls(urls):
    """
    Remove duplicate URLs while preserving important variations.

    Args:
        urls (list): List of URLs to deduplicate

    Returns:
        list: Deduplicated URLs
    """
    # Normalize all URLs first
    normalized_urls = []
    url_map = defaultdict(list)  # Map normalized URLs to original URLs

    for url in urls:
        normalized = normalize_url(url)
        normalized_urls.append(normalized)
        url_map[normalized].append(url)

    # Return unique normalized URLs
    return list(set(normalized_urls))

def merge_static_results(jadx_results, apkleaks_results, mobsf_results):
    """
    Merge results from different static analysis tools.

    Args:
        jadx_results (dict): Results from JADX analysis
        apkleaks_results (dict): Results from APKLeaks analysis
        mobsf_results (dict): Results from MobSF analysis

    Returns:
        dict: Merged and normalized results
    """
    # Collect all URLs from different sources
    all_urls = []

    # Add URLs from JADX
    if 'urls' in jadx_results:
        all_urls.extend(jadx_results['urls'])

    # Add URLs from APKLeaks
    if 'urls' in apkleaks_results:
        all_urls.extend(apkleaks_results['urls'])

    # Add URLs from MobSF
    if 'urls' in mobsf_results:
        all_urls.extend(mobsf_results['urls'])

    # Deduplicate URLs
    unique_urls = deduplicate_urls(all_urls)

    # Process URLs to extract parameters and normalize
    normalized_entries = []
    for url in unique_urls:
        normalized_url, parameters = extract_path_parameters(url)

        # Create entry with metadata
        entry = {
            'url': normalized_url,
            'original_url': url,
            'parameters': parameters,
            'sources': []
        }

        # Determine which sources contributed this URL
        if url in jadx_results.get('urls', []):
            entry['sources'].append('jadx')
        if url in apkleaks_results.get('urls', []):
            entry['sources'].append('apkleaks')
        if url in mobsf_results.get('urls', []):
            entry['sources'].append('mobsf')

        normalized_entries.append(entry)

    # Collect domains
    domains = set()
    if 'domains' in jadx_results:
        domains.update(jadx_results['domains'])
    if 'domains' in apkleaks_results:
        domains.update(apkleaks_results['domains'])
    if 'domains' in mobsf_results:
        domains.update(mobsf_results['domains'])

    # Collect endpoints
    endpoints = set()
    if 'endpoints' in jadx_results:
        endpoints.update(jadx_results['endpoints'])
    if 'endpoints' in apkleaks_results:
        endpoints.update(apkleaks_results['endpoints'])
    if 'endpoints' in mobsf_results:
        endpoints.update(mobsf_results['endpoints'])

    # Collect secrets
    secrets = []
    if 'secrets' in apkleaks_results:
        secrets.extend(apkleaks_results['secrets'])

    # Collect permissions
    permissions = []
    if 'permissions' in mobsf_results:
        permissions.extend(mobsf_results['permissions'])

    # Collect certificates
    certificates = []
    if 'certificates' in mobsf_results:
        certificates.extend(mobsf_results['certificates'])

    return {
        'urls': normalized_entries,
        'domains': list(domains),
        'endpoints': list(endpoints),
        'secrets': secrets,
        'permissions': permissions,
        'certificates': certificates
    }

def generate_url_map(merged_results):
    """
    Generate a comprehensive URL map from merged results.

    Args:
        merged_results (dict): Merged results from all static analysis tools

    Returns:
        dict: Structured URL map
    """
    url_map = {
        'entries': [],
        'domains': merged_results.get('domains', []),
        'endpoints': merged_results.get('endpoints', []),
        'secrets': merged_results.get('secrets', []),
        'permissions': merged_results.get('permissions', []),
        'certificates': merged_results.get('certificates', []),
        'summary': {
            'total_urls': len(merged_results.get('urls', [])),
            'unique_domains': len(merged_results.get('domains', [])),
            'endpoints_count': len(merged_results.get('endpoints', [])),
            'secrets_count': len(merged_results.get('secrets', [])),
            'permissions_count': len(merged_results.get('permissions', []))
        }
    }

    # Process URL entries
    for entry in merged_results.get('urls', []):
        # Parse URL components
        try:
            parsed = urlparse(entry['url'])
            url_entry = {
                'signature': f"{parsed.netloc}{parsed.path}",
                'host': parsed.netloc,
                'path': parsed.path,
                'method': 'UNKNOWN',  # Will be determined during dynamic analysis
                'parameters': entry['parameters'],
                'sources': entry['sources'],
                'original_urls': [entry['original_url']],
                'risk_level': 'UNKNOWN'
            }

            # Determine risk level based on URL content
            risk_indicators = [
                'admin', 'login', 'auth', 'token', 'password', 'secret',
                'key', 'config', 'debug', 'test', 'dev'
            ]

            risk_level = 'LOW'
            for indicator in risk_indicators:
                if indicator in entry['url'].lower():
                    risk_level = 'HIGH'
                    break
                elif any(indicator in param.get('value', '').lower() for param in entry['parameters']):
                    risk_level = 'MEDIUM'
                    break

            url_entry['risk_level'] = risk_level
            url_map['entries'].append(url_entry)

        except Exception as e:
            print(f"Error processing URL entry {entry}: {e}")
            continue

    return url_map

# Example usage
if __name__ == "__main__":
    # Sample data for testing
    jadx_results = {
        "urls": [
            "https://api.example.com/v1/users/123",
            "https://api.example.com/v1/products",
            "https://cdn.example.com/assets/image.png"
        ],
        "domains": ["api.example.com", "cdn.example.com"],
        "endpoints": []
    }

    apkleaks_results = {
        "urls": [
            "https://api.example.com/v1/login",
            "https://api.example.com/v1/users/456"
        ],
        "endpoints": ["/api/v1/login", "/api/v1/register"],
        "secrets": ["API_KEY=abc123"]
    }

    mobsf_results = {
        "urls": [
            "https://api.example.com/v1/users/789",
            "https://external-service.com/api/data"
        ],
        "domains": ["external-service.com"],
        "permissions": ["android.permission.INTERNET"],
        "certificates": []
    }

    # Merge results
    merged = merge_static_results(jadx_results, apkleaks_results, mobsf_results)
    print("Merged Results:")
    print(json.dumps(merged, indent=2))

    # Generate URL map
    url_map = generate_url_map(merged)
    print("\nURL Map:")
    print(json.dumps(url_map, indent=2))