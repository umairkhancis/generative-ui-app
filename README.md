# Generative UI App

A demo app that puts a CopilotKit chat in front of two interchangeable AI agent backends — Google ADK (Gemini) and LangGraph (OpenAI). Switch between them with a single line of frontend code.

## Stack

- **Frontend** — React 19 + Vite 6 + Tailwind 4, CopilotKit chat UI
- **Runtime** — Node + Hono, multiplexes the two agent backends behind one HTTP endpoint
- **Backend** — Python 3.12 + FastAPI, two separate processes:
  - Google ADK `LlmAgent` running Gemini 2.0 Flash
  - LangChain `create_agent` running OpenAI `gpt-4.1` over LangGraph

## How it fits together

```
Browser ──► Vite :5173
              └── /api/copilotkit ──► CopilotKit runtime :4002
                                        ├── agentId "default" ──► LangGraph :8000
                                        └── agentId "gemini"  ──► ADK       :8009
```

The browser only ever talks to Vite. Vite proxies CopilotKit calls to the Node runtime, which then routes to whichever Python backend the React app asked for via its `agentId`.

## Prerequisites

- **Python 3.12** (`brew install python@3.12` on macOS)
- **Node 20+**
- API keys: `OPENAI_API_KEY` (LangGraph backend) and `GOOGLE_API_KEY` (ADK backend)

## Setup

### 1. Backend

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# edit .env and fill in OPENAI_API_KEY and GOOGLE_API_KEY
```

### 2. Frontend

```bash
cd frontend
npm install
```

## Run

You need **three terminals** — one per process. None of them daemonize themselves.

**Terminal 1 — ADK backend (Gemini)**
```bash
cd backend
.venv/bin/python main_adk.py
# serves http://localhost:8009
```

**Terminal 2 — LangGraph backend (OpenAI)**
```bash
cd backend
.venv/bin/python main_langgraph.py
# serves http://localhost:8000
```

**Terminal 3 — Frontend (Vite + CopilotKit runtime)**
```bash
cd frontend
npm run dev
# Vite at http://localhost:5173, CopilotKit runtime at :4002
```

Open http://localhost:5173.

### Stopping everything

```bash
for p in 8000 8009 4002 5173; do kill -9 $(lsof -ti:$p) 2>/dev/null; done
```

## Switching agents

Edit `frontend/src/App.tsx`:

```ts
export const agentId = "default";  // LangGraph (OpenAI)
// export const agentId = "gemini";  // ADK (Gemini)
```

The mapping `agentId → backend URL` lives in `frontend/server.ts`. Add a new agent by adding a new entry there and a matching FastAPI process.

## Configuration

Override backend URLs without code changes:

```bash
LANGGRAPH_DEPLOYMENT_URL=http://other-host:8000 \
ADK_AGENT_URL=http://other-host:8009 \
npm run dev
```

## Project layout

```
backend/
  main_adk.py         # ADK + Gemini, FastAPI on :8009
  main_langgraph.py   # LangGraph + OpenAI, FastAPI on :8000
  helper.py           # notebook helpers (not used by servers)
  requirements.txt
  .env.example
frontend/
  server.ts           # CopilotKit runtime, routes agentId → backend
  watch-server.ts     # auto-restarts server.ts on edit
  vite.config.ts      # proxies /api/copilotkit → :4002
  src/
    App.tsx           # picks the agent via `agentId`
    main.tsx          # CopilotKit provider
    error-boundary.tsx
    global.css
CLAUDE.md             # notes for Claude Code
```

## Common issues

- **`openai.RateLimitError: insufficient_quota`** — your OpenAI account has no credit. Either add billing, or switch to the `gemini` agent in `App.tsx` to bypass OpenAI entirely.
- **`ModuleNotFoundError` on backend startup** — the venv is using the system Python (often 3.9). `copilotkit` requires Python 3.10+; this repo is set up for 3.12. Recreate the venv with `python3.12 -m venv .venv`.
- **`INCOMPLETE_STREAM` in the chat UI** — the upstream Python backend errored mid-stream. Check that backend's terminal for the real traceback.
- **Port already in use** — run the kill snippet above before starting again.

## Tests

Playwright is wired up but the `e2e/` directory is currently empty.

```bash
cd frontend
npm run test:e2e
```
