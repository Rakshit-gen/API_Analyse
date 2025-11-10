from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import DebuggerState
from tools import decode_jwt_token, make_http_request, test_oauth_flow
from config import get_settings

settings = get_settings()

AUTH_TROUBLESHOOTER_PROMPT = """You are the Auth Troubleshooter Agent. Debug authentication and authorization.

CHECK:
- Bearer token format and placement
- JWT token validity (expiry, signature, claims)
- API key location (header, query, cookie)
- OAuth2 flow issues (grant types, scopes)
- Basic auth encoding
- CORS and preflight requests

Identify specific auth issues and token problems."""

llm = ChatGroq(
    model=settings.model_name,
    temperature=settings.temperature,
    api_key=settings.groq_api_key
).bind_tools([decode_jwt_token, make_http_request, test_oauth_flow])


def auth_troubleshooter_node(state: DebuggerState) -> DebuggerState:
    """Troubleshoot authentication issues."""
    try:
        request = state.get("api_request", {})
        response = state.get("api_response", {})
        auth_type = state.get("auth_type")
        
        auth_header = request.get("headers", {}).get("Authorization", "")
        
        messages = [
            SystemMessage(content=AUTH_TROUBLESHOOTER_PROMPT),
            HumanMessage(content=f"Debug authentication:\nAuth Type: {auth_type}\nAuth Header: {auth_header}\nStatus: {response.get('status_code')}\nError: {response.get('body', '')}")
        ]
        
        ai_response = llm.invoke(messages)
        
        analysis = {
            "auth_type": auth_type,
            "auth_header_present": bool(auth_header),
            "status_code": response.get("status_code"),
            "is_auth_error": response.get("status_code") in [401, 403],
            "diagnosis": ai_response.content
        }
        
        # Decode JWT if present
        if "bearer" in auth_header.lower() and len(auth_header.split()) > 1:
            token = auth_header.split()[1]
            try:
                jwt_info = decode_jwt_token.invoke({"token": token})
                analysis["jwt_details"] = jwt_info
            except:
                pass
        
        state["analysis_results"]["auth_analysis"] = analysis
        
        # Update root cause if auth issue
        if analysis["is_auth_error"] and not state.get("root_cause"):
            state["root_cause"] = f"Authentication failed: {ai_response.content[:200]}"
        
        return state
        
    except Exception as e:
        state["analysis_results"]["auth_analysis"] = {"error": str(e)}
        return state
