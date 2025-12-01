#!/usr/bin/env python3
"""
GET TOKEN HELPER
================
Lấy JWT token để test API

Usage:
    python get_token.py                     # Default: 49.01.104.145 / 123456
    python get_token.py <username> <pass>   # Custom credentials
    
Output sẽ là access token, có thể dùng với curl:
    curl -H "Authorization: Bearer $(python get_token.py)" http://localhost:8000/api/sv/profile
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

# Default credentials
DEFAULT_USERNAME = "49.01.104.145"
DEFAULT_PASSWORD = "123456"

def get_token(username: str, password: str) -> dict:
    """Get JWT tokens from login endpoint"""
    url = f"{BASE_URL}/api/auth/login"
    data = json.dumps({
        "tenDangNhap": username,
        "matKhau": password
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {"error": f"HTTP {e.code}", "detail": error_body}
    except urllib.error.URLError as e:
        return {"error": "Connection failed", "detail": str(e.reason)}

def main():
    # Parse args
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = DEFAULT_USERNAME
        password = DEFAULT_PASSWORD
    
    # Check for --full flag to print full response
    full_output = "--full" in sys.argv
    
    result = get_token(username, password)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        print(f"Detail: {result.get('detail', 'N/A')}", file=sys.stderr)
        sys.exit(1)
    
    if full_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Just print access token for easy piping
        # Response format: { isSuccess, data: { token, refreshToken, user } }
        if result.get("isSuccess") and result.get("data"):
            print(result["data"].get("token", ""))
        else:
            print(result.get("access", ""))

if __name__ == "__main__":
    main()
