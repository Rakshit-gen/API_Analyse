from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import DebuggerState
from tools import make_http_request, validate_json_schema
from config import get_settings

settings = get_settings()

REQUEST_ANALYZER_PROMPT = """You are the Request Analyzer Agent. Examine API requests for issues.

CHECK:
- HTTP method correctness (GET/POST/PUT/PATCH/DELETE)
- URL structure and encoding
- Required headers (Content-Type, Accept, Authorization)
- Query parameter format
- Request body structure and encoding
- Content-Type matching body format

Analyze the provided request and identify any structural issues."""

llm = ChatGroq(
    model=settings.model_name,
    temperature=settings.temperature,
    api_key=settings.groq_api_key
).bind_tools([make_http_request, validate_json_schema])


def request_analyzer_node(state: DebuggerState) -> DebuggerState:
    """Analyze API request structure."""
    try:
        request = state.get("api_request", {})
        
        messages = [
            SystemMessage(content=REQUEST_ANALYZER_PROMPT),
            HumanMessage(content=f"Analyze this API request:\n{request}\n\nIdentify any issues with method, URL, headers, or body structure.")
        ]
        
        response = llm.invoke(messages)
        
        analysis = {
            "method": request.get("method"),
            "url": request.get("url"),
            "headers_present": bool(request.get("headers")),
            "body_present": bool(request.get("body")),
            "content_type": request.get("headers", {}).get("Content-Type"),
            "issues_found": response.content
        }
        
        state["analysis_results"]["request_analysis"] = analysis
        return state
        
    except Exception as e:
        state["analysis_results"]["request_analysis"] = {"error": str(e)}
        return state
