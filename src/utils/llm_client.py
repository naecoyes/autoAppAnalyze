#!/usr/bin/env python3
"""
LLM Client for Auto APK Analyzer
"""

import json
import os
import requests

# Load API keys
api_keys = {}
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'api_keys.json')) as f:
        api_keys = json.load(f)
except FileNotFoundError:
    print("Warning: api_keys.json not found")

class LLMClient:
    def __init__(self, service_name):
        """
        Initialize LLM client for a specific service.

        Args:
            service_name (str): Name of the LLM service
        """
        self.service_name = service_name
        self.api_key = api_keys.get(service_name, "")
        self.is_configured = bool(self.api_key)

    def query(self, prompt, **kwargs):
        """
        Query the LLM service with a prompt.

        Args:
            prompt (str): The prompt to send to the LLM
            **kwargs: Additional arguments for the specific service

        Returns:
            str: Response from the LLM service
        """
        if not self.is_configured:
            return f"Error: {self.service_name} API key not configured"

        try:
            if self.service_name == "perplexity":
                return self._query_perplexity(prompt, **kwargs)
            elif self.service_name == "gemini":
                return self._query_gemini(prompt, **kwargs)
            elif self.service_name == "chatgpt":
                return self._query_chatgpt(prompt, **kwargs)
            elif self.service_name == "modelscope":
                return self._query_modelscope(prompt, **kwargs)
            elif self.service_name == "openrouter":
                return self._query_openrouter(prompt, **kwargs)
            else:
                return f"Error: Unsupported service {self.service_name}"
        except Exception as e:
            return f"Error querying {self.service_name}: {e}"

    def _query_perplexity(self, prompt, **kwargs):
        """Query Perplexity API."""
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": kwargs.get("model", "llama-3-sonar-large-32k-online"),
            "messages": [
                {"role": "system", "content": "You are a mobile app security analyst. Help identify APIs and endpoints in mobile applications."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _query_gemini(self, prompt, **kwargs):
        """Query Gemini API."""
        # Gemini API endpoint (example)
        model = kwargs.get("model", "gemini-pro")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [{
                "parts": [{
                    "text": f"You are a mobile app security analyst. Help identify APIs and endpoints in mobile applications.\n\n{prompt}"
                }]
            }]
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    def _query_chatgpt(self, prompt, **kwargs):
        """Query ChatGPT API."""
        # OpenAI API endpoint
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": kwargs.get("model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "You are a mobile app security analyst. Help identify APIs and endpoints in mobile applications."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _query_modelscope(self, prompt, **kwargs):
        """Query ModelScope API."""
        # ModelScope API endpoint
        model = kwargs.get("model", "qwen-max")  # Default to Qwen model
        url = f"https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "input": {
                "messages": [
                    {"role": "system", "content": "You are a mobile app security analyst. Help identify APIs and endpoints in mobile applications."},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "max_tokens": kwargs.get("max_tokens", 2000),
                "temperature": kwargs.get("temperature", 0.7)
            }
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["output"]["text"]

    def _query_openrouter(self, prompt, **kwargs):
        """Query OpenRouter API."""
        # OpenRouter API endpoint
        model = kwargs.get("model", "openrouter/auto")  # Default to auto model selection
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a mobile app security analyst. Help identify APIs and endpoints in mobile applications."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

class AppDiscoveryClient:
    def __init__(self):
        """Initialize clients for all supported LLM services."""
        self.clients = {
            "perplexity": LLMClient("perplexity"),
            "gemini": LLMClient("gemini"),
            "chatgpt": LLMClient("chatgpt"),
            "modelscope": LLMClient("modelscope"),
            "openrouter": LLMClient("openrouter")
        }

    def discover_apps(self, query):
        """
        Discover mobile apps using LLM services.

        Args:
            query (str): Query about mobile apps to discover

        Returns:
            dict: Results from different LLM services
        """
        results = {}

        discovery_prompt = f"""
        Based on the following query, identify popular mobile applications that might be relevant:

        Query: {query}

        Please provide:
        1. A list of 5-10 relevant mobile applications
        2. For each app, provide:
           - Package name (for Android) or bundle ID (for iOS)
           - Brief description of the app's functionality
           - Likely API endpoints the app might use
           - Potential security considerations

        Format your response as a structured list.
        """

        for service_name, client in self.clients.items():
            if client.is_configured:
                print(f"Querying {service_name} for app discovery...")
                results[service_name] = client.query(discovery_prompt)
            else:
                results[service_name] = f"API key not configured for {service_name}"

        return results

    def analyze_app_apis(self, app_info):
        """
        Analyze potential APIs for a given app using LLM services.

        Args:
            app_info (str): Information about the app to analyze

        Returns:
            dict: Analysis results from different LLM services
        """
        results = {}

        analysis_prompt = f"""
        Based on the following app information, analyze what APIs and endpoints this app might use:

        App Information: {app_info}

        Please provide:
        1. Likely API endpoints (URLs) the app might communicate with
        2. Common HTTP methods used (GET, POST, PUT, DELETE, etc.)
        3. Expected request/response formats
        4. Authentication mechanisms that might be used
        5. Potential hidden or undocumented endpoints
        6. Security considerations for these APIs

        Format your response as a structured analysis.
        """

        for service_name, client in self.clients.items():
            if client.is_configured:
                print(f"Querying {service_name} for API analysis...")
                results[service_name] = client.query(analysis_prompt)
            else:
                results[service_name] = f"API key not configured for {service_name}"

        return results

# Example usage
if __name__ == "__main__":
    # Example of using the AppDiscoveryClient
    discovery_client = AppDiscoveryClient()

    # Example app discovery query
    query = "mobile banking applications in Southeast Asia"
    print("Discovering apps based on query:", query)
    discovery_results = discovery_client.discover_apps(query)

    for service, result in discovery_results.items():
        print(f"\n{service.upper()} Results:")
        print(result[:500] + "..." if len(result) > 500 else result)

    # Example API analysis
    app_info = "Package: com.example.bankapp\nFunctionality: Mobile banking with account management, transfers, and bill payments"
    print("\n\nAnalyzing APIs for app:", app_info)
    analysis_results = discovery_client.analyze_app_apis(app_info)

    for service, result in analysis_results.items():
        print(f"\n{service.upper()} Analysis:")
        print(result[:500] + "..." if len(result) > 500 else result)