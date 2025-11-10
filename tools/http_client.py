import httpx
import time
from typing import Optional, Dict, Any
from langchain_core.tools import tool


@tool
def make_http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """Make an HTTP request and return detailed response information.
    
    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        url: Target URL
        headers: Request headers
        body: Request body (JSON)
        params: Query parameters
        timeout: Request timeout in seconds
    """
    try:
        start_time = time.time()
        
        with httpx.Client(timeout=timeout) as client:
            response = client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=body,
                params=params
            )
        
        elapsed = time.time() - start_time
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "elapsed_seconds": round(elapsed, 3),
            "success": 200 <= response.status_code < 300,
            "error": None
        }
    except Exception as e:
        return {
            "status_code": 0,
            "headers": {},
            "body": "",
            "elapsed_seconds": 0,
            "success": False,
            "error": str(e)
        }


@tool
def test_oauth_flow(
    token_url: str,
    client_id: str,
    client_secret: str,
    grant_type: str = "client_credentials",
    scope: Optional[str] = None
) -> Dict[str, Any]:
    """Test OAuth2 authentication flow.
    
    Args:
        token_url: OAuth token endpoint
        client_id: Client ID
        client_secret: Client secret
        grant_type: OAuth grant type
        scope: Requested scope
    """
    try:
        data = {
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret
        }
        if scope:
            data["scope"] = scope
        
        with httpx.Client(timeout=30) as client:
            response = client.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                "success": True,
                "access_token": token_data.get("access_token"),
                "token_type": token_data.get("token_type"),
                "expires_in": token_data.get("expires_in"),
                "scope": token_data.get("scope"),
                "error": None
            }
        else:
            return {
                "success": False,
                "access_token": None,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "access_token": None,
            "error": str(e)
        }
