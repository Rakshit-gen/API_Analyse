from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import DebuggerState
from tools import parse_openapi_spec, validate_json_schema
from config import get_settings

settings = get_settings()

SCHEMA_VALIDATOR_PROMPT = """You are the Schema Validator Agent. Ensure API contract compliance.

CHECK:
- OpenAPI/Swagger spec compliance
- Required vs optional fields
- Data type mismatches
- Format validations (email, uuid, date)
- Enum value compliance
- Nested object structure

Identify schema violations and contract mismatches."""

llm = ChatGroq(
    model=settings.model_name,
    temperature=settings.temperature,
    api_key=settings.groq_api_key
).bind_tools([parse_openapi_spec, validate_json_schema])


def schema_validator_node(state: DebuggerState) -> DebuggerState:
    """Validate API request/response against schema."""
    try:
        request = state.get("api_request", {})
        openapi_spec = state.get("openapi_spec")
        
        messages = [
            SystemMessage(content=SCHEMA_VALIDATOR_PROMPT),
            HumanMessage(content=f"Validate request body:\n{request.get('body')}\n\nAgainst OpenAPI spec: {openapi_spec is not None}")
        ]
        
        ai_response = llm.invoke(messages)
        
        analysis = {
            "has_spec": openapi_spec is not None,
            "request_body": request.get("body"),
            "validation_result": ai_response.content
        }
        
        state["analysis_results"]["schema_validation"] = analysis
        return state
        
    except Exception as e:
        state["analysis_results"]["schema_validation"] = {"error": str(e)}
        return state
