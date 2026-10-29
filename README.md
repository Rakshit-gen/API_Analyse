# API_Analyse

You have an API call that fails. You paste in what you sent, what came back and a sentence about the problem. A small team of LLM agents looks at the request, the response, the auth and the schema, then writes up the likely root cause and a fix with code.

Built with LangGraph, FastAPI and Llama 3.3 70B on Groq. There is a web front end at https://api-analyse-fe.vercel.app ([source](https://github.com/Rakshit-gen/api_analyse_fe)) and a terminal version in `main.py`.

## How it works

The agents are nodes in a LangGraph graph. A supervisor node sits in the middle and every other node hands control back to it.

```
            +-----------------+
   start -> |   supervisor    | -> FINISH
            +-----------------+
              |   ^     ^   |
              v   |     |   v
  request_analyzer   response_parser   auth_troubleshooter   schema_validator
              \           |                  |                 /
               +----------+---- solution_generator -----------+
```

The supervisor's routing is plain rules, not a model call:

1. If a solution exists, finish.
2. If two analyses are done, go to `solution_generator`.
3. Otherwise run the first one that applies and has not run yet:
   - `request_analyzer` if you sent a request
   - `response_parser` if you sent a response
   - `auth_troubleshooter` if the status was 401 or 403
   - `schema_validator` if you sent an OpenAPI spec
4. If none apply, go straight to `solution_generator`.

Keeping routing in code means a run always ends, in at most four steps, and you can predict which agents ran.

What each agent does:

| Agent | Looks at | Notes |
|---|---|---|
| `request_analyzer` | method, URL, headers, body | Flags missing content type, wrong method and the like |
| `response_parser` | status code, body, error text | Explains what the server is complaining about |
| `auth_troubleshooter` | auth type, `Authorization` header, status | Decodes a bearer JWT locally and adds its claims and expiry to the result |
| `schema_validator` | request and response vs. your OpenAPI spec | Only runs when you pass a spec |
| `solution_generator` | everything above | Writes the root cause and numbered fix steps |

`tools/` holds LangChain tools for making HTTP requests, decoding JWTs, validating JSON Schema and reading OpenAPI specs. They are bound to the agents, but today only the JWT decoder is actually called during a run. The HTTP tool is used by `/test-request`.

## Quickstart

You need Python 3.11+ and a [Groq API key](https://console.groq.com/keys).

```bash
git clone https://github.com/Rakshit-gen/API_Analyse.git
cd API_Analyse
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "GROQ_API_KEY=gsk_..." > .env
uvicorn api.main:app --reload
```

Then send it a problem:

```bash
curl -X POST http://localhost:8000/debug \
  -H "Content-Type: application/json" \
  -d @examples/example_request.json
```

Or use the interactive terminal version: `python main.py`.

## API

### `POST /debug`

```json
{
  "issue_description": "Getting 401 when creating a user",
  "api_request": {
    "method": "POST",
    "url": "https://api.example.com/users",
    "headers": {"Authorization": "Bearer eyJ...", "Content-Type": "application/json"},
    "body": {"name": "John"}
  },
  "api_response": {"status_code": 401, "body": "{\"error\": \"Invalid token\"}"},
  "auth_type": "bearer"
}
```

Only `issue_description` is required. `openapi_spec` and `auth_credentials` are optional too.

Response:

```json
{
  "root_cause": "Authentication failed: the JWT expired at ...",
  "solution": "1. Request a new access token ...\n2. ...",
  "analysis_results": {
    "request_analysis": {"...": "..."},
    "auth_analysis": {"jwt_details": {"...": "..."}, "diagnosis": "..."}
  },
  "status": "completed"
}
```

### `POST /test-request`

Sends the request you describe (`method`, `url`, `headers`, `body`, `params`) from the server and returns the result. Useful to check a fix.

### `GET /health`

`{"status": "healthy", "service": "api-debugger"}`

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `GROQ_API_KEY` | required | Groq key |
| `MODEL_NAME` | `llama-3.3-70b-versatile` | Model for all agents |
| `TEMPERATURE` | `0.1` | Sampling temperature |
| `MAX_TOKENS` | `2000` | Max tokens per reply |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | Only used by `python api/main.py` |

## Deploy

`render.yaml` is ready for Render. Create a Blueprint from the repo and set `GROQ_API_KEY`.

## Layout

```
api/main.py       FastAPI app
main.py           interactive CLI
graph/workflow.py LangGraph wiring
graph/state.py    shared state passed between nodes
agents/           supervisor and the five specialists
tools/            HTTP, JWT and schema tools
config.py         settings from env
```

## Limits

- The JWT decoder reads claims without checking the signature. It tells you what is in the token, not whether it is valid.
- `/test-request` will call any URL you give it, including internal addresses. Do not expose it publicly without an allow list.
- Whatever you paste, including tokens and API keys, is sent to Groq as part of the prompt.
- CORS is open to every origin.
- No streaming yet. `/debug` returns once the whole graph has run, usually in a few seconds.
