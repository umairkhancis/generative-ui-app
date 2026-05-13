# Generative UI App

A focused demo of **controlled generative UI** and **shared agent state** with CopilotKit. Theme: a Talabat-style food-delivery ordering journey — discover → menu → cart (live canvas) → checkout → tracking — backed by a CSV "database" and a LangGraph (OpenAI) agent.

## Stack

- **Frontend** — React 19 + Vite 6 + Tailwind 4, CopilotKit chat UI
- **Runtime** — Node + Hono, exposes the agent over `/api/copilotkit`
- **Backend** — Python 3.12 + FastAPI: LangChain `create_agent` over LangGraph, running OpenAI `gpt-4.1`. Pure-Python food-delivery domain lives in `backend/food/` (no framework deps).

## How it fits together

```
Browser ──► Vite :5173
              └── /api/copilotkit ──► CopilotKit Node runtime :4002
                                        └── LangGraph backend :8000
```

The browser only ever talks to Vite. Vite proxies CopilotKit calls to the Node runtime, which forwards them to the Python agent.

## Prerequisites

- **Python 3.12** (`brew install python@3.12` on macOS)
- **Node 22+** (for `--watch` and `--env-file-if-exists`)
- `OPENAI_API_KEY`

## Setup

### 1. Backend

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# edit .env and fill in OPENAI_API_KEY
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # default points LANGGRAPH_DEPLOYMENT_URL at localhost:8000
```

## Run

The project Makefile is the simplest path:

```bash
make restart   # kill any leftover ports, start LangGraph + frontend
make logs      # tail combined logs
```

Or, manually in two terminals:

```bash
# Terminal 1
cd backend && .venv/bin/python main.py

# Terminal 2
cd frontend && npm run dev
```

Open http://localhost:5173.

## Configuration

`frontend/server.ts` reads `LANGGRAPH_DEPLOYMENT_URL` from `frontend/.env` (loaded via Node's `--env-file-if-exists`). Point it at a remote LangGraph deployment by editing the file:

```
LANGGRAPH_DEPLOYMENT_URL=https://my-langgraph.example.com
```

There is no hardcoded fallback — the server throws at startup if it's unset.

## What to read first

If you want to understand CopilotKit's two key primitives:

- **Controlled GenUI** — `frontend/src/hooks/use-controlled-components.tsx`. One screen of `useComponent({ name, description, parameters, render })` registrations. The agent calls these by name; the runtime renders them inline in chat.
- **Shared state** — `backend/agent/state.py` declares the shared fields on `AgentState`. Tools mutate via `Command(update={cart: ...})`; the React side reads with `useAgent(...).state.cart` and writes with `.setState(...)`. The cart card is registered as a controlled component AND subscribes to that same shared state — so the agent and the UI converge on a single source of truth.

## Project layout

```
backend/
  food/                 # pure-Python food-delivery package (no framework deps)
    __init__.py
    catalog.py          # CSV-backed restaurant & menu queries
    cart.py             # pure cart operations
    orders.py           # placement + time-progressed status
    _seed.py            # regenerates db/ CSVs
    db/
      restaurants.csv
      menu_items.csv
  agent/                # LangGraph + CopilotKit wiring (state, tools, prompt, graph)
  main.py               # FastAPI entry — mounts the assembled agent
  requirements.txt
  .env.example
frontend/
  server.ts             # CopilotKit Node runtime
  vite.config.ts        # proxies /api/copilotkit → :4002
  src/
    App.tsx             # CartPanel side panel (canvas), reads/writes agent.state.cart
    main.tsx            # CopilotKit provider
    hooks/
      use-controlled-components.tsx
      use-example-suggestions.tsx
    components/         # registered GenUI components + side panel
    lib/cart.ts         # shared cart math (mirrors backend snapshot)
  .env.example
CLAUDE.md               # notes for Claude Code agents
```

## Common issues

- **`LANGGRAPH_DEPLOYMENT_URL is not set`** — copy `frontend/.env.example` to `frontend/.env`.
- **`openai.RateLimitError: insufficient_quota`** — your OpenAI account has no credit; add billing.
- **`ModuleNotFoundError` on backend startup** — the venv is using the system Python. `copilotkit` requires 3.10+; this repo is set up for 3.12. Recreate the venv with `python3.12 -m venv .venv`.
- **`INCOMPLETE_STREAM` in the chat UI** — the Python backend errored mid-stream. Tail `scripts/.logs/langgraph.log` for the real traceback.
- **Port already in use** — `make restart`.
- **`InvalidUpdateError: At key 'cart'`** — two writes to the same state channel in one LangGraph tick. The repo handles this by annotating `cart`/`todos` with a `_last_write_wins` reducer. If you add new shared-state fields, do the same.
