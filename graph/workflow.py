from langgraph.graph import StateGraph, END
from graph.state import DebuggerState
from agents import (
    supervisor_node,
    request_analyzer_node,
    response_parser_node,
    auth_troubleshooter_node,
    schema_validator_node,
    solution_generator_node
)


def route_agent(state: DebuggerState) -> str:
    """Route to next agent based on supervisor decision."""
    return state.get("next_agent", "FINISH")


def create_workflow():
    """Create and compile the debugging workflow."""
    workflow = StateGraph(DebuggerState)
    
    # Add all agent nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("request_analyzer", request_analyzer_node)
    workflow.add_node("response_parser", response_parser_node)
    workflow.add_node("auth_troubleshooter", auth_troubleshooter_node)
    workflow.add_node("schema_validator", schema_validator_node)
    workflow.add_node("solution_generator", solution_generator_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_agent,
        {
            "request_analyzer": "request_analyzer",
            "response_parser": "response_parser",
            "auth_troubleshooter": "auth_troubleshooter",
            "schema_validator": "schema_validator",
            "solution_generator": "solution_generator",
            "FINISH": END
        }
    )
    
    # All agents return to supervisor
    workflow.add_edge("request_analyzer", "supervisor")
    workflow.add_edge("response_parser", "supervisor")
    workflow.add_edge("auth_troubleshooter", "supervisor")
    workflow.add_edge("schema_validator", "supervisor")
    workflow.add_edge("solution_generator", "supervisor")
    
    # Compile with recursion limit
    return workflow.compile()