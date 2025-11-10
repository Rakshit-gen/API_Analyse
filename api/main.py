from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage
from graph import create_workflow
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Integration Debugger",
    description="Multi-agent system for debugging API integration issues",
    version="1.0.0"
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class APIRequest(BaseModel):
    method: str = Field(..., description="HTTP method")
    url: str = Field(..., description="API endpoint URL")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None


class APIResponse(BaseModel):
    status_code: int
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    body: Optional[str] = None
    error: Optional[str] = None


class DebugRequest(BaseModel):
    issue_description: str = Field(..., description="Description of the API issue")
    api_request: Optional[APIRequest] = None
    api_response: Optional[APIResponse] = None
    openapi_spec: Optional[Dict[str, Any]] = None
    auth_type: Optional[str] = None
    auth_credentials: Optional[Dict[str, str]] = None


class DebugResponse(BaseModel):
    root_cause: str
    solution: str
    analysis_results: Dict[str, Any]
    status: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-debugger"}


@app.post("/debug", response_model=DebugResponse)
async def debug_api_issue(request: DebugRequest):
    """Main debugging endpoint - analyzes API issues using multi-agent system."""
    try:
        workflow = create_workflow()
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=request.issue_description)],
            "api_request": request.api_request.dict() if request.api_request else {},
            "api_response": request.api_response.dict() if request.api_response else {},
            "openapi_spec": request.openapi_spec,
            "auth_type": request.auth_type,
            "auth_credentials": request.auth_credentials,
            "analysis_results": {},
            "root_cause": "",
            "solution": "",
            "next_agent": "supervisor"
        }
        
        # Run workflow
        logger.info(f"Starting debug workflow for: {request.issue_description[:100]}")
        final_state = workflow.invoke(initial_state)
        
        return DebugResponse(
            root_cause=final_state.get("root_cause", "Analysis completed"),
            solution=final_state.get("solution", "No solution generated"),
            analysis_results=final_state.get("analysis_results", {}),
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Error in debug workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-request")
async def test_request(request: APIRequest):
    """Test an API request directly using the HTTP client tool."""
    try:
        from tools import make_http_request
        
        result = make_http_request.invoke({
            "method": request.method,
            "url": request.url,
            "headers": request.headers,
            "body": request.body,
            "params": request.params
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    from config import get_settings
    
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
