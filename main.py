#!/usr/bin/env python3
"""CLI interface for API Integration Debugger."""

import json
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage
from graph import create_workflow


def load_json_file(filepath: str):
    """Load JSON from file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def main():
    """Interactive CLI for debugging API issues."""
    print("=" * 60)
    print("API Integration Debugger - Multi-Agent System")
    print("=" * 60)
    print()
    
    # Get issue description
    print("Describe your API issue:")
    issue = input("> ").strip()
    
    if not issue:
        print("Error: Issue description is required")
        sys.exit(1)
    
    # Optional: Load request/response from files
    api_request = {}
    api_response = {}
    
    print("\nDo you have an API request file? (path or press Enter to skip):")
    request_file = input("> ").strip()
    if request_file and Path(request_file).exists():
        api_request = load_json_file(request_file) or {}
    
    print("\nDo you have an API response file? (path or press Enter to skip):")
    response_file = input("> ").strip()
    if response_file and Path(response_file).exists():
        api_response = load_json_file(response_file) or {}
    
    # Initialize workflow
    print("\n" + "=" * 60)
    print("Starting multi-agent analysis...")
    print("=" * 60 + "\n")
    
    workflow = create_workflow()
    
    initial_state = {
        "messages": [HumanMessage(content=issue)],
        "api_request": api_request,
        "api_response": api_response,
        "openapi_spec": None,
        "auth_type": None,
        "auth_credentials": None,
        "analysis_results": {},
        "root_cause": "",
        "solution": "",
        "next_agent": "supervisor"
    }
    
    # Run workflow with streaming
    try:
        for step, state in enumerate(workflow.stream(initial_state), 1):
            node_name = list(state.keys())[0]
            print(f"[Step {step}] Agent: {node_name}")
            
            if node_name == "solution_generator":
                print("\n" + "=" * 60)
                print("SOLUTION GENERATED")
                print("=" * 60)
        
        # Get final state
        final_state = workflow.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("ROOT CAUSE")
        print("=" * 60)
        print(final_state.get("root_cause", "Not identified"))
        
        print("\n" + "=" * 60)
        print("SOLUTION")
        print("=" * 60)
        print(final_state.get("solution", "No solution generated"))
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
