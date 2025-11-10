import base64
import json
from typing import Dict, Any
from datetime import datetime
from langchain_core.tools import tool


@tool
def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token without verification to inspect its contents.
    
    Args:
        token: JWT token string
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return {"error": "Invalid JWT format. Expected 3 parts separated by dots."}
        
        # Decode header
        header_data = parts[0] + '=' * (4 - len(parts[0]) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_data))
        
        # Decode payload
        payload_data = parts[1] + '=' * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_data))
        
        # Check expiry
        exp = payload.get('exp')
        is_expired = False
        time_remaining = None
        
        if exp:
            exp_time = datetime.fromtimestamp(exp)
            now = datetime.now()
            is_expired = now > exp_time
            time_remaining = (exp_time - now).total_seconds() if not is_expired else 0
        
        return {
            "header": header,
            "payload": payload,
            "algorithm": header.get("alg"),
            "is_expired": is_expired,
            "expiry_timestamp": exp,
            "time_remaining_seconds": time_remaining,
            "issuer": payload.get("iss"),
            "subject": payload.get("sub"),
            "audience": payload.get("aud"),
            "error": None
        }
    except Exception as e:
        return {"error": f"Failed to decode JWT: {str(e)}"}
