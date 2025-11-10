from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import DebuggerState
from config import get_settings

settings = get_settings()

SOLUTION_GENERATOR_PROMPT = """You are the Solution Generator Agent. Provide actionable fixes.

GENERATE:
1. Root cause summary
2. Step-by-step fix instructions
3. Corrected code examples (curl, Python requests)
4. Testing strategy
5. Prevention tips

FORMAT: Clear, executable solutions with code blocks. Be concise and actionable."""

llm = ChatGroq(
    model=settings.model_name,
    temperature=0.2,
    max_tokens=settings.max_tokens,
    api_key=settings.groq_api_key
)


def solution_generator_node(state: DebuggerState) -> DebuggerState:
    """Generate comprehensive solution."""
    try:
        analysis = state.get("analysis_results", {})
        root_cause = state.get("root_cause", "Unknown issue")
        
        context = f"""
Root Cause: {root_cause}

Analysis Results:
- Request: {analysis.get('request_analysis', {}).get('issues_found', 'No issues')}
- Response: {analysis.get('response_analysis', {}).get('analysis', 'No analysis')}
- Auth: {analysis.get('auth_analysis', {}).get('diagnosis', 'Not checked')}
- Schema: {analysis.get('schema_validation', {}).get('validation_result', 'Not validated')}

Original Request: {state.get('api_request', {})}
Response: {state.get('api_response', {})}
"""
        
        messages = [
            SystemMessage(content=SOLUTION_GENERATOR_PROMPT),
            HumanMessage(content=f"Generate a complete solution:\n{context}")
        ]
        
        response = llm.invoke(messages)
        
        state["solution"] = response.content
        state["next_agent"] = "FINISH"
        
        return state
        
    except Exception as e:
        state["solution"] = f"Error generating solution: {str(e)}"
        state["next_agent"] = "FINISH"
        return state
