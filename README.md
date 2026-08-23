# API Integration Debugger

A multi-agent system built with LangGraph for debugging API integration issues. It uses specialized agents to analyze requests, responses, authentication, and schemas, then generates actionable fixes.

## Features

- 6 specialized AI agents working together
- HTTP request and response analysis
- JWT, OAuth2, and API key debugging
- OpenAPI and JSON schema validation
- Real HTTP request testing
- Streaming agent progress
- FastAPI backend
- CLI interface
- Type-safe request handling
- CORS support
- Cloud deployment support

## Architecture

```text
User Request
     │
     ▼
Supervisor Agent
     │
     ├───────────────┬────────────────┐
     ▼               ▼                ▼
Request Analyzer  Response Parser  Auth Troubleshooter
     │               │                │
     └───────────────┼────────────────┘
                     ▼
              Schema Validator
                     │
                     ▼
             Solution Generator
                     │
                     ▼
               Final Solution
````

### Agents

1. **Supervisor Agent**
   Routes the debugging workflow to the appropriate specialized agents.

2. **Request Analyzer**
   Checks HTTP methods, headers, request bodies, URLs, and request structure.

3. **Response Parser**
   Analyzes HTTP status codes, response bodies, error messages, and API failures.

4. **Auth Troubleshooter**
   Debugs authentication issues involving JWT, OAuth2, and API keys.

5. **Schema Validator**
   Validates request and response structures against JSON Schema and OpenAPI definitions.

6. **Solution Generator**
   Combines the analysis from previous agents and produces an actionable solution with code examples.

## Tools

The agents use specialized tools during debugging:

* `make_http_request` for executing HTTP requests
* `decode_jwt_token` for inspecting JWT payloads and claims
* `validate_json_schema` for JSON schema validation
* `parse_openapi_spec` for extracting OpenAPI definitions
* `test_oauth_flow` for OAuth2 flow testing

## Tech Stack

* Python 3.11+
* LangGraph
* FastAPI
* Groq
* Llama 3.3 70B
* Pydantic
* JWT
* OpenAPI
* JSON Schema

## Quick Start

### Prerequisites

* Python 3.11+
* Groq API key

Get a Groq API key from [Groq Console](https://console.groq.com).

### Installation

```bash
git clone https://github.com/Rakshit-gen/API_Analyse.git
cd API_Analyse

python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Add your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0.1
MAX_TOKENS=2000
PORT=8000
HOST=0.0.0.0
```

## Running the API

Start the FastAPI server:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Or:

```bash
cd api
python main.py
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## CLI

The project also includes an interactive CLI:

```bash
python main.py
```

Follow the prompts to describe the API issue and provide the request and response details.

## API Endpoints

### POST `/debug`

Main debugging endpoint.

#### Request

```json
{
  "issue_description": "Getting 401 error when calling the API",
  "api_request": {
    "method": "POST",
    "url": "https://api.example.com/users",
    "headers": {
      "Authorization": "Bearer token123",
      "Content-Type": "application/json"
    },
    "body": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  "api_response": {
    "status_code": 401,
    "body": "{\"error\": \"Invalid token\"}"
  },
  "auth_type": "bearer"
}
```

#### Response

```json
{
  "root_cause": "JWT token is expired",
  "solution": "1. Request a new access token...\n2. Update your authorization header...",
  "analysis_results": {
    "request_analysis": {},
    "response_analysis": {},
    "auth_analysis": {}
  },
  "status": "completed"
}
```

### POST `/test-request`

Executes an API request through the debugging service.

#### Request

```json
{
  "method": "GET",
  "url": "https://api.example.com/users",
  "headers": {
    "Authorization": "Bearer token123"
  }
}
```

### GET `/health`

Health check endpoint.

#### Response

```json
{
  "status": "healthy",
  "service": "api-debugger"
}
```

## Example Scenarios

### Expired JWT

```bash
curl -X POST http://localhost:8000/debug \
  -H "Content-Type: application/json" \
  -d '{
    "issue_description": "Getting 401 unauthorized error",
    "api_response": {
      "status_code": 401,
      "body": "Token expired"
    },
    "auth_type": "bearer"
  }'
```

The system analyzes the response and authentication configuration, identifies the likely JWT expiration issue, and suggests the required fix.

### Schema Validation Error

```bash
curl -X POST http://localhost:8000/debug \
  -H "Content-Type: application/json" \
  -d '{
    "issue_description": "API returns 400 bad request",
    "api_request": {
      "method": "POST",
      "url": "https://api.example.com/users",
      "body": {
        "name": "John",
        "age": "twenty"
      }
    },
    "api_response": {
      "status_code": 400,
      "body": "Invalid age format"
    }
  }'
```

The schema validator identifies the type mismatch and the solution generator produces a corrected request.

### CORS Error

```bash
curl -X POST http://localhost:8000/debug \
  -H "Content-Type: application/json" \
  -d '{
    "issue_description": "CORS error in browser console",
    "api_response": {
      "error": "CORS policy blocked"
    }
  }'
```

The system analyzes the error and identifies the likely CORS configuration issue.

## Frontend Integration

The backend exposes a REST API designed to work as a standalone microservice.

A frontend can:

1. Send an API issue to `/debug`
2. Stream agent progress
3. Display individual analysis results
4. Show the detected root cause
5. Display the generated solution
6. Test API requests through `/test-request`

Example:

```javascript
const response = await fetch("http://localhost:8000/debug", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    issue_description: userInput,
    api_request: requestData,
    api_response: responseData
  })
});

const result = await response.json();

console.log(result.root_cause);
console.log(result.solution);
```

## Project Structure

```text
API_Analyse/
├── agents/
│   ├── supervisor.py
│   ├── request_analyzer.py
│   ├── response_parser.py
│   ├── auth_troubleshooter.py
│   ├── schema_validator.py
│   └── solution_generator.py
│
├── graph/
│   ├── state.py
│   └── workflow.py
│
├── tools/
│   ├── http_client.py
│   ├── jwt_decoder.py
│   └── schema_validator_tool.py
│
├── api/
│   └── main.py
│
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## Deployment

The service is designed for deployment on platforms such as Render.

Create `render.yaml`:

```yaml
services:
  - type: web
    name: api-debugger
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
```

Push the repository to GitHub, create a web service on Render, add `GROQ_API_KEY` as an environment variable, and deploy.

## Environment Variables

| Variable       | Description             | Default                   |
| -------------- | ----------------------- | ------------------------- |
| `GROQ_API_KEY` | Groq API key            | Required                  |
| `MODEL_NAME`   | LLM model               | `llama-3.3-70b-versatile` |
| `TEMPERATURE`  | LLM temperature         | `0.1`                     |
| `MAX_TOKENS`   | Maximum response tokens | `2000`                    |
| `PORT`         | Server port             | `8000`                    |
| `HOST`         | Server host             | `0.0.0.0`                 |

## Security

* Keep API keys in environment variables.
* Never commit `.env` files.
* Validate incoming request data.
* Configure CORS for your production frontend.
* Rate limit public API endpoints.
* Avoid logging sensitive authentication credentials.
* Treat JWTs and API keys as sensitive request data.

## Testing

Check the service health:

```bash
curl http://localhost:8000/health
```

Run a debugging request:

```bash
curl -X POST http://localhost:8000/debug \
  -H "Content-Type: application/json" \
  -d @examples/request.json
```

## Troubleshooting

### Module Not Found

Make sure the virtual environment is active and dependencies are installed:

```bash
pip install -r requirements.txt
```

### Missing Groq API Key

Check your `.env` file:

```bash
cat .env
```

Make sure `GROQ_API_KEY` is configured.

### Port Already in Use

Run the server on another port:

```bash
PORT=8001 python -m uvicorn api.main:app
```

## License

MIT License.

## Links

Demo: [Live](https://api-analyse-fe.vercel.app/)
Repository: [GitHub](https://github.com/Rakshit-gen/API_Analyse)

Built with [LangGraph](https://github.com/langchain-ai/langgraph), [FastAPI](https://fastapi.tiangolo.com/), and [Groq](https://groq.com/).

