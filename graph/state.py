from typing import TypedDict, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator


class DebuggerState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    api_request: dict
    api_response: dict
    openapi_spec: Optional[dict]
    auth_type: Optional[str]
    auth_credentials: Optional[dict]
    analysis_results: dict
    root_cause: str
    solution: str
    next_agent: str
