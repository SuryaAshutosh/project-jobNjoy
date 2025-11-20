"""
Example of how agents should authenticate when calling endpoints
"""

import hashlib
import hmac
import json
import requests

def generate_agent_signature(payload, secret):
    """
    Generate a signature for agent requests
    
    Args:
        payload: The request payload (string)
        secret: The shared secret key
        
    Returns:
        str: Generated signature
    """
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def make_authenticated_agent_request(url, payload, secret):
    """
    Make an authenticated request to an agent endpoint
    
    Args:
        url: The endpoint URL
        payload: The request payload (dict)
        secret: The shared secret key
        
    Returns:
        requests.Response: The response
    """
    # Convert payload to JSON string
    payload_str = json.dumps(payload, separators=(',', ':'))
    
    # Generate signature
    signature = generate_agent_signature(payload_str, secret)
    
    # Make request with signature in header
    headers = {
        'Content-Type': 'application/json',
        'X-Signature': signature
    }
    
    response = requests.post(url, data=payload_str, headers=headers)
    return response

# Example usage
if __name__ == "__main__":
    # Agent configuration
    agent_secret = "your-agent-secret-key"
    endpoint_url = "http://localhost:8000/api/agents/register-run"
    
    # Request payload
    payload = {
        "agent_id": "scraper-001",
        "run_data": {
            "source": "linkedin",
            "job_count": 50
        }
    }
    
    # Make authenticated request
    response = make_authenticated_agent_request(endpoint_url, payload, agent_secret)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")