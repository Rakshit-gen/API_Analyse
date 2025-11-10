import jsonschema
import httpx
from typing import Dict, Any, Optional
from langchain_core.tools import tool


@tool
def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate JSON data against a JSON schema.
    
    Args:
        data: JSON data to validate
        schema: JSON schema to validate against
    """
    try:
        jsonschema.validate(instance=data, schema=schema)
        return {
            "valid": True,
            "errors": [],
            "message": "Data is valid according to the schema"
        }
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "errors": [{
                "message": e.message,
                "path": list(e.path),
                "validator": e.validator,
                "schema_path": list(e.schema_path)
            }],
            "message": f"Validation failed: {e.message}"
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [],
            "message": f"Error during validation: {str(e)}"
        }


@tool
def parse_openapi_spec(
    endpoint: str,
    method: str,
    spec_url: Optional[str] = None,
    spec_dict: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Parse OpenAPI specification to extract schema for a specific endpoint.
    
    Args:
        endpoint: API endpoint path (e.g., /users/{id})
        method: HTTP method (get, post, put, delete)
        spec_url: URL to OpenAPI spec (JSON or YAML)
        spec_dict: OpenAPI spec as dictionary
    """
    try:
        if spec_url:
            response = httpx.get(spec_url, timeout=10)
            spec = response.json()
        elif spec_dict:
            spec = spec_dict
        else:
            return {"error": "Either spec_url or spec_dict must be provided"}
        
        paths = spec.get("paths", {})
        endpoint_spec = paths.get(endpoint, {})
        method_spec = endpoint_spec.get(method.lower(), {})
        
        if not method_spec:
            return {"error": f"Endpoint {method.upper()} {endpoint} not found in spec"}
        
        # Extract request schema
        request_body = method_spec.get("requestBody", {})
        request_schema = None
        if request_body:
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            request_schema = json_content.get("schema")
        
        # Extract response schema
        responses = method_spec.get("responses", {})
        response_schema = None
        success_response = responses.get("200") or responses.get("201")
        if success_response:
            content = success_response.get("content", {})
            json_content = content.get("application/json", {})
            response_schema = json_content.get("schema")
        
        # Extract parameters
        parameters = method_spec.get("parameters", [])
        required_params = [p["name"] for p in parameters if p.get("required")]
        
        return {
            "endpoint": endpoint,
            "method": method.upper(),
            "request_schema": request_schema,
            "response_schema": response_schema,
            "parameters": parameters,
            "required_parameters": required_params,
            "description": method_spec.get("description", ""),
            "error": None
        }
    except Exception as e:
        return {"error": f"Failed to parse OpenAPI spec: {str(e)}"}
