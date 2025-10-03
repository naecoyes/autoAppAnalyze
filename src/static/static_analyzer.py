#!/usr/bin/env python3
"""
Static Analysis Module for Auto APK Analyzer
"""

import subprocess
import os
import json
import re
from pathlib import Path

# Load configuration
config = {}
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')) as f:
        config = json.load(f)
except FileNotFoundError:
    print("Warning: config.json not found, using default paths")

# Get tool paths from config or use defaults
JADX_PATH = config.get('tools', {}).get('jadx', 'jadx')
APKLEAKS_PATH = config.get('tools', {}).get('apkleaks', 'apkleaks')
MOBSF_PATH = config.get('tools', {}).get('mobsf', 'mobsf')

def run_jadx_extraction(apk_path):
    """
    Run JADX to extract strings and potential URLs from an APK.

    Args:
        apk_path (str): Path to the APK file

    Returns:
        dict: Extracted URLs and strings
    """
    print(f"Running JADX extraction on {apk_path}")

    # Create output directory for JADX results
    apk_dir = Path(apk_path).parent
    jadx_output_dir = apk_dir / "jadx_output"
    jadx_output_dir.mkdir(exist_ok=True)

    try:
        # Run JADX to decompile APK
        # Using --no-src to skip Java source generation for faster processing
        # Using --output-dir to specify output directory
        jadx_cmd = [
            JADX_PATH,
            "--no-src",  # Skip Java source generation
            "--output-dir", str(jadx_output_dir),
            apk_path
        ]

        print(f"Executing: {' '.join(jadx_cmd)}")
        result = subprocess.run(jadx_cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"JADX failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return {"urls": [], "domains": [], "endpoints": [], "error": "JADX failed"}

        # Extract URLs from JADX output
        urls, domains = extract_urls_from_jadx_output(jadx_output_dir)

        results = {
            "urls": urls,
            "domains": domains,
            "endpoints": [],
            "jadx_output_dir": str(jadx_output_dir)
        }

        return results

    except subprocess.TimeoutExpired:
        print("JADX execution timed out")
        return {"urls": [], "domains": [], "endpoints": [], "error": "JADX timeout"}
    except Exception as e:
        print(f"Error running JADX: {e}")
        return {"urls": [], "domains": [], "endpoints": [], "error": str(e)}

def extract_urls_from_jadx_output(jadx_output_dir):
    """
    Extract URLs and domains from JADX output files.

    Args:
        jadx_output_dir (Path): Path to JADX output directory

    Returns:
        tuple: (urls, domains) lists
    """
    urls = []
    domains = []

    # URL regex pattern
    url_pattern = re.compile(
        r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    )

    # Domain regex pattern
    domain_pattern = re.compile(
        r'(?:https?://)?(?:[-\w.])+(?:\.[a-zA-Z]{2,})'
    )

    # Search for URLs in all text files in JADX output
    for file_path in jadx_output_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.txt', '.xml', '.json', '.js', '.html', '.cfg', '']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Find URLs
                    found_urls = url_pattern.findall(content)
                    urls.extend(found_urls)

                    # Find domains
                    found_domains = domain_pattern.findall(content)
                    domains.extend([d.replace('http://', '').replace('https://', '') for d in found_domains])

            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

    # Remove duplicates
    urls = list(set(urls))
    domains = list(set(domains))

    return urls, domains

def run_apkleaks_scan(apk_path):
    """
    Run APKLeaks to scan for URIs, endpoints, and secrets.

    Args:
        apk_path (str): Path to the APK file

    Returns:
        dict: Scan results
    """
    print(f"Running APKLeaks scan on {apk_path}")

    try:
        # Create temporary output file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            output_file = tmp_file.name

        # Run APKLeaks scan
        # Using --json to get structured output
        apkleaks_cmd = [
            APKLEAKS_PATH,
            "-f", apk_path,
            "--json",
            "-o", output_file
        ]

        print(f"Executing: {' '.join(apkleaks_cmd)}")
        result = subprocess.run(apkleaks_cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"APKLeaks failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            # Clean up temporary file
            if os.path.exists(output_file):
                os.remove(output_file)
            return {"urls": [], "endpoints": [], "secrets": [], "error": "APKLeaks failed"}

        # Parse APKLeaks output
        results = parse_apkleaks_output_file(output_file)

        # Clean up temporary file
        if os.path.exists(output_file):
            os.remove(output_file)

        return results

    except subprocess.TimeoutExpired:
        print("APKLeaks execution timed out")
        return {"urls": [], "endpoints": [], "secrets": [], "error": "APKLeaks timeout"}
    except Exception as e:
        print(f"Error running APKLeaks: {e}")
        return {"urls": [], "endpoints": [], "secrets": [], "error": str(e)}

def parse_apkleaks_output_file(output_file):
    """
    Parse APKLeaks output file to extract findings.

    Args:
        output_file (str): Path to APKLeaks output file

    Returns:
        dict: Parsed results
    """
    try:
        # Read the output file
        with open(output_file, 'r') as f:
            data = json.load(f)

        results = {
            "urls": [],
            "endpoints": [],
            "secrets": []
        }

        # Extract URLs and endpoints from findings
        if "links" in data:
            results["urls"] = data["links"]

        if "endpoints" in data:
            results["endpoints"] = data["endpoints"]

        if "secrets" in data:
            results["secrets"] = data["secrets"]

        return results

    except json.JSONDecodeError as e:
        print(f"Error parsing APKLeaks JSON output: {e}")
        return {"urls": [], "endpoints": [], "secrets": [], "error": "JSON parse error"}
    except FileNotFoundError:
        print(f"APKLeaks output file not found: {output_file}")
        return {"urls": [], "endpoints": [], "secrets": [], "error": "Output file not found"}
    except Exception as e:
        print(f"Error parsing APKLeaks output: {e}")
        return {"urls": [], "endpoints": [], "secrets": [], "error": str(e)}

def parse_apkleaks_output(output):
    """
    Parse APKLeaks output to extract findings.

    Args:
        output (str): APKLeaks output

    Returns:
        dict: Parsed results
    """
    try:
        # Try to parse as JSON if it's JSON output
        data = json.loads(output)

        results = {
            "urls": [],
            "endpoints": [],
            "secrets": []
        }

        # Extract URLs and endpoints from findings
        if "links" in data:
            results["urls"] = data["links"]

        if "endpoints" in data:
            results["endpoints"] = data["endpoints"]

        if "secrets" in data:
            results["secrets"] = data["secrets"]

        return results

    except json.JSONDecodeError:
        # If not JSON, try to parse as text
        lines = output.split('\n')
        urls = []
        endpoints = []
        secrets = []

        url_pattern = re.compile(r'https?://[^\s]+')
        endpoint_pattern = re.compile(r'/(?:[^\s/]+/)*[^\s]*')

        for line in lines:
            # Extract URLs
            found_urls = url_pattern.findall(line)
            urls.extend(found_urls)

            # Extract potential endpoints
            found_endpoints = endpoint_pattern.findall(line)
            endpoints.extend(found_endpoints)

        # Remove duplicates
        urls = list(set(urls))
        endpoints = list(set(endpoints))

        return {
            "urls": urls,
            "endpoints": endpoints,
            "secrets": secrets
        }

def run_mobsf_scan(apk_path):
    """
    Run MobSF scan on an APK (requires MobSF server).

    Args:
        apk_path (str): Path to the APK file

    Returns:
        dict: MobSF scan results
    """
    print(f"Running MobSF scan on {apk_path}")

    try:
        # Import requests for HTTP calls
        import requests
        import time

        # Start MobSF server in background
        mobsf_process = subprocess.Popen([
            MOBSF_PATH,
            "-b", "127.0.0.1:8000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for server to start
        time.sleep(10)

        # Upload APK file
        with open(apk_path, 'rb') as f:
            files = {'file': f}
            upload_response = requests.post('http://127.0.0.1:8000/api/v1/upload', files=files)

        if upload_response.status_code != 200:
            print(f"Failed to upload APK to MobSF: {upload_response.status_code}")
            mobsf_process.terminate()
            return {"urls": [], "domains": [], "certificates": [], "permissions": [], "error": "Upload failed"}

        upload_data = upload_response.json()
        scan_hash = upload_data.get('hash')

        if not scan_hash:
            print("Failed to get scan hash from MobSF upload response")
            mobsf_process.terminate()
            return {"urls": [], "domains": [], "certificates": [], "permissions": [], "error": "No scan hash"}

        # Start static analysis
        scan_data = {'hash': scan_hash}
        scan_response = requests.post('http://127.0.0.1:8000/api/v1/scan', data=scan_data)

        if scan_response.status_code != 200:
            print(f"Failed to start MobSF scan: {scan_response.status_code}")
            mobsf_process.terminate()
            return {"urls": [], "domains": [], "certificates": [], "permissions": [], "error": "Scan start failed"}

        # Wait for scan to complete
        time.sleep(30)

        # Get scan results
        report_response = requests.get(f'http://127.0.0.1:8000/api/v1/report_json', params={'hash': scan_hash})

        if report_response.status_code != 200:
            print(f"Failed to get MobSF report: {report_response.status_code}")
            mobsf_process.terminate()
            return {"urls": [], "domains": [], "certificates": [], "permissions": [], "error": "Report failed"}

        report_data = report_response.json()

        # Extract relevant information from report
        results = {
            "urls": [],
            "domains": [],
            "certificates": [],
            "permissions": []
        }

        # Extract URLs from network_security_config and other sources
        if 'network_security' in report_data:
            for entry in report_data['network_security'].get('certificates', []):
                results['certificates'].append(entry)

        # Extract domains from URLs found in the app
        if 'urls' in report_data:
            for url in report_data['urls']:
                results['urls'].append(url)
                # Extract domain from URL
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    if parsed.netloc:
                        results['domains'].append(parsed.netloc)
                except:
                    pass

        # Extract permissions
        if 'permissions' in report_data:
            results['permissions'] = list(report_data['permissions'].keys())

        # Clean up - terminate MobSF server
        mobsf_process.terminate()

        return results

    except Exception as e:
        print(f"Error running MobSF scan: {e}")
        try:
            mobsf_process.terminate()
        except:
            pass
        return {"urls": [], "domains": [], "certificates": [], "permissions": [], "error": str(e)}

# Example usage
if __name__ == "__main__":
    # This would typically be called with an actual APK path
    sample_apk = "sample.apk"
    print("Running static analysis modules...")

    jadx_results = run_jadx_extraction(sample_apk)
    print("JADX Results:", json.dumps(jadx_results, indent=2))

    apkleaks_results = run_apkleaks_scan(sample_apk)
    print("APKLeaks Results:", json.dumps(apkleaks_results, indent=2))