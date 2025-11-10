from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import DebuggerState
from config import get_settings

settings = get_settings()

SUPERVISOR_PROMPT = """You are the Supervisor Agent coordinating API debugging. Analyze the user's issue and route to specialized agents.

ROUTING LOGIC:
- If request structure unclear → request_analyzer
- If response/error unclear → response_parser
- If auth issues suspected (401, 403, token errors) → auth_troubleshooter
- If schema/contract issues (400, validation errors) → schema_validator
- If enough analysis done (3+ agents completed) → solution_generator
- If solution generated → FINISH

Current analysis status:
{analysis_status}

Always respond with the next agent name: request_analyzer, response_parser, auth_troubleshooter, schema_validator, solution_generator, or FINISH."""

llm = ChatGroq(
    model=settings.model_name,
    temperature=settings.temperature,
    api_key=settings.groq_api_key
)


def supervisor_node(state: DebuggerState) -> DebuggerState:
    """Supervisor agent that routes to specialized agents."""
    try:
        analysis = state.get("analysis_results", {})
        completed = [k for k, v in analysis.items() if v]
        
        # Check if we have a solution
        if state.get("solution"):
            state["next_agent"] = "FINISH"
            return state
        
        # If we have enough analysis, go to solution (reduced from 3 to 2)
        if len(completed) >= 2:
            state["next_agent"] = "solution_generator"
            return state
        
        # Prevent infinite loops - check what hasn't been done yet
        pending_agents = []
        if "request_analysis" not in completed and state.get("api_request"):
            pending_agents.append("request_analyzer")
        if "response_analysis" not in completed and state.get("api_response"):
            pending_agents.append("response_parser")
        if "auth_analysis" not in completed and state.get("api_response", {}).get("status_code") in [401, 403]:
            pending_agents.append("auth_troubleshooter")
        if "schema_validation" not in completed and state.get("openapi_spec"):
            pending_agents.append("schema_validator")
        
        # If no pending agents, go to solution
        if not pending_agents:
            state["next_agent"] = "solution_generator"
            return state
        
        # Route to first pending agent
        state["next_agent"] = pending_agents[0]
        return state
        
    except Exception as e:
        state["next_agent"] = "FINISH"
        state["root_cause"] = f"Supervisor error: {str(e)}"
        return state