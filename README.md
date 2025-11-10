# API Integration Debugger 🔍

A production-ready multi-agent system built with LangGraph for debugging API integration issues. Uses specialized AI agents to analyze requests, responses, authentication, and schemas to provide actionable solutions.

## 🌟 Features

- **Multi-Agent Architecture**: 6 specialized agents working together
- **Comprehensive Analysis**: Request structure, response parsing, auth debugging, schema validation
- **RESTful API**: FastAPI backend ready for microservice deployment
- **Real-time Processing**: Streaming agent progress
- **Production Ready**: Type-safe, error handling, CORS enabled
- **Easy Deployment**: Optimized for Render and other cloud platforms

## 🏗️ Architecture

```
User Request → Supervisor Agent
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
Request Analyzer  Response Parser  Auth Troubleshooter
    ↓               ↓               ↓
    └───────────────┼───────────────┘
                    ↓
              Schema Validator
                    ↓
            Solution Generator
                    ↓
              Final Solution
```

### Agents

1. **Supervisor Agent**: Routes workflow to specialized agents
2. **Request Analyzer**: Validates HTTP method, headers, body structure
3. **Response Parser**: Interprets status codes and error messages
4. **Auth Troubleshooter**: Debugs JWT, OAuth2, API keys
5. **Schema Validator**: Ensures OpenAPI/Swagger compliance
6. **Solution Generator**: Creates actionable fixes with code examples

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Groq API key ([Get one here](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone <your-repo>
cd api-debugger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Configuration

Edit `.env`:

```env
GROQ_API_KEY=your_actual_groq_api_key
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0.1
MAX_TOKENS=2000
PORT=8000
HOST=0.0.0.0
```

## 📖 Usage

### 1. FastAPI Server (Recommended for Frontend Integration)

Start the server:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Or:

```bash
cd api
python main.py
```

API will be available at `http://localhost:8000`

**API Documentation**: `http://localhost:8000/docs`

### 2. CLI Interface

```bash
python main.py
```

Follow the interactive prompts.

## 🔌 API Endpoints

### POST /debug

Main debugging endpoint.

**Request Body:**

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

**Response:**

```json
{
  "root_cause": "JWT token is expired",
  "solution": "1. Request a new access token...\n2. Update your authorization header...",
  "analysis_results": {
    "request_analysis": {...},
    "response_analysis": {...},
    "auth_analysis": {...}
  },
  "status": "completed"
}
```

### POST /test-request

Test an API request directly.

**Request Body:**

```json
{
  "method": "GET",
  "url": "https://api.example.com/users",
  "headers": {
    "Authorization": "Bearer token123"
  }
}
```

### GET /health

Health check endpoint.

```json
{
  "status": "healthy",
  "service": "api-debugger"
}
```

## 🎯 Example Scenarios

### Scenario 1: Expired JWT Token

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

### Scenario 2: Schema Validation Error

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

### Scenario 3: CORS Error

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

## 🌐 Deploying on Render

### 1. Create `render.yaml`

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

### 2. Deploy

1. Push code to GitHub
2. Connect repository in Render dashboard
3. Add `GROQ_API_KEY` environment variable
4. Deploy!

Your API will be live at: `https://your-app.onrender.com`

## 🛠️ Tools Available to Agents

1. **make_http_request**: Execute HTTP requests
2. **decode_jwt_token**: Analyze JWT tokens
3. **validate_json_schema**: Validate against JSON schemas
4. **parse_openapi_spec**: Extract OpenAPI specifications
5. **test_oauth_flow**: Test OAuth2 authentication

## 📦 Project Structure

```
api-debugger/
├── agents/              # AI agent implementations
│   ├── supervisor.py
│   ├── request_analyzer.py
│   ├── response_parser.py
│   ├── auth_troubleshooter.py
│   ├── schema_validator.py
│   └── solution_generator.py
├── graph/               # LangGraph workflow
│   ├── state.py
│   └── workflow.py
├── tools/               # Agent tools
│   ├── http_client.py
│   ├── jwt_decoder.py
│   └── schema_validator_tool.py
├── api/                 # FastAPI application
│   └── main.py
├── config.py            # Configuration
├── main.py              # CLI interface
└── requirements.txt     # Dependencies
```

## 🔒 Security Notes

- Never commit `.env` file
- Use environment variables for sensitive data
- Configure CORS properly for production
- Validate all inputs in production
- Rate limit the API endpoints

## 🧪 Testing

```bash
# Test the API
curl http://localhost:8000/health

# Run a debug request
curl -X POST http://localhost:8000/debug \
  -H "Content-Type: application/json" \
  -d @examples/request.json
```

## 🤝 Integration with Frontend

This backend is designed as a microservice. Your frontend can:

1. Call `/debug` endpoint with API issues
2. Display real-time agent progress
3. Show analysis results and solutions
4. Test API requests via `/test-request`

**Example Frontend Integration:**

```javascript
const response = await fetch('http://localhost:8000/debug', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    issue_description: userInput,
    api_request: requestData,
    api_response: responseData
  })
});

const result = await response.json();
console.log(result.solution);
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| GROQ_API_KEY | Groq API key (required) | - |
| MODEL_NAME | LLM model name | llama-3.3-70b-versatile |
| TEMPERATURE | LLM temperature | 0.1 |
| MAX_TOKENS | Max tokens per response | 2000 |
| PORT | Server port | 8000 |
| HOST | Server host | 0.0.0.0 |

## 🐛 Troubleshooting

**Issue**: Module not found error
```bash
# Make sure you're in the right directory and venv is activated
pip install -r requirements.txt
```

**Issue**: GROQ_API_KEY not found
```bash
# Check your .env file exists and has the key
cat .env
```

**Issue**: Port already in use
```bash
# Change PORT in .env or use different port
PORT=8001 python -m uvicorn api.main:app
```

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Groq](https://groq.com)
- Framework: [FastAPI](https://fastapi.tiangolo.com)

---

**Made with ❤️ for developers debugging APIs**
#   A P I _ A n a l y s e  
 