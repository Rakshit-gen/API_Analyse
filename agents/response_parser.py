from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import DebuggerState
from tools import make_http_request, validate_json_schema
from config import get_settings

settings = get_settings()

RESPONSE_PARSER_PROMPT = """You are the Response Parser Agent. Analyze API responses and errors.

CHECK:
- HTTP status codes (2xx, 4xx, 5xx meanings)
- Error message interpretation
- Response header analysis
- Content-Type vs actual body
- Timeout and connection errors
- Rate limiting (429 status)

Provide root cause analysis of response issues."""

llm = ChatGroq(
    model=settings.model_name,
    temperature=settings.temperature,
    api_key=settings.groq_api_key
).bind_tools([make_http_request, validate_json_schema])


def response_parser_node(state: DebuggerState) -> DebuggerState:
    """Parse and analyze API response."""
    try:
        response = state.get("api_response", {})
        
        messages = [
            SystemMessage(content=RESPONSE_PARSER_PROMPT),
            HumanMessage(content=f"Analyze this API response:\n{response}\n\nWhat is the root cause of any errors?")
        ]
        
        ai_response = llm.invoke(messages)
        
        status = response.get("status_code", 0)
        analysis = {
            "status_code": status,
            "status_category": "success" if 200 <= status < 300 else "client_error" if 400 <= status < 500 else "server_error",
            "error_message": response.get("error") or response.get("body"),
            "headers": response.get("headers", {}),
            "analysis": ai_response.content
        }
        
        state["analysis_results"]["response_analysis"] = analysis
        
        # Set root cause if not already set
        if not state.get("root_cause") and status >= 400:
            state["root_cause"] = f"HTTP {status}: {ai_response.content[:200]}"
        
        return state
        
    except Exception as e:
        state["analysis_results"]["response_analysis"] = {"error": str(e)}
        return state
