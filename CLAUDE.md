# CLAUDE.md

Guidance for Claude Code when working with this repo.

## Architecture

One runtime per layer, three ports:

```
Browser → Vite (5173)
            └── proxy /api/copilotkit → CopilotKit Node runtime (4002, Hono)
                                          └── agentId "default" → LangGraph backend (8000, Python/FastAPI)
```

- **`backend/main_langgraph.py`** (`:8000`) — LangChain `create_agent` (OpenAI `gpt-4.1`) wrapped with `CopilotKitMiddleware` and a `MemorySaver` checkpointer, exposed via `add_langgraph_fastapi_endpoint(path="/")`. Framework wiring only — domain logic lives in `backend/food/`.
- **`backend/food/`** — pure-Python food-delivery package (no framework deps). `catalog.py` reads the CSV "db" at `food/db/`. `cart.py` and `orders.py` are pure functions over snapshots. `_seed.py` regenerates the CSVs.
- **`frontend/server.ts`** — defines a `CopilotRuntime` with one agent (`default` → LangGraph). Run by `node --watch --import tsx/esm server.ts` (built-in Node watch, no custom watcher).
- **`frontend/src/App.tsx`** — `agentId = "default"`. Reads/writes shared agent state (`cart`, `todos`) via `useAgent`. Side panel renders `CartPanel` (canvas-mode shared state); `TodoList` is kept commented for reference.
- **`frontend/src/hooks/use-controlled-components.tsx`** — registers controlled GenUI components via `useComponent`: restaurant/menu cards + carousels, cart summary card (also a canvas — subscribes to `agent.state.cart`), order confirmation, order tracking.
- **`frontend/vite.config.ts`** — proxies `/api/copilotkit` → `localhost:4002` so the React app talks to the Node runtime, never directly to Python.

The runtime URL is overridable via `LANGGRAPH_DEPLOYMENT_URL` (loaded from `frontend/.env`; see `.env.example`).

## Commands

### Backend (Python 3.12 — copilotkit requires ≥3.10)

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # then fill OPENAI_API_KEY
.venv/bin/python main_langgraph.py   # LangGraph on :8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # default LANGGRAPH_DEPLOYMENT_URL=http://localhost:8000
npm run dev      # Node runtime on :4002 + Vite on :5173
npm run build    # vite production build
npm run preview  # serve the build
npm run test:e2e # playwright (testDir ./e2e — currently empty)
```

`npm run dev` runs `node --env-file-if-exists=.env --watch --import tsx/esm server.ts & vite`. Editing `server.ts` triggers Node's built-in watch to restart the runtime.

### Restarting the whole stack

Use the project Makefile from the repo root:

```bash
make restart   # kill all ports, restart langgraph + frontend
make logs      # tail combined logs
```

## CopilotKit primitives at play

This codebase is deliberately small so the primitives stand out:

- **Controlled GenUI** — `useComponent({ name, description, parameters, render })` registers a React component the LLM can call by name. Registrations live in `frontend/src/hooks/use-controlled-components.tsx`.
- **Shared state** — fields on `AgentState` (in `main_langgraph.py`) are auto-synced both ways. Frontend reads via `useAgent({agentId:"default"}).state.<field>` and writes via `.setState({<field>: ...})`. Tools write via `Command(update={<field>: ...})`. The `cart` channel uses a `_last_write_wins` reducer to allow concurrent updates from both sides in the same LangGraph tick.
- **Canvas-mode component** — `CartSummaryCard` is registered via `useComponent` (controlled GenUI) AND subscribes to `agent.state.cart` via `useAgent` (shared state). Same is true of the side `CartPanel`. They render the same source of truth.

## Gotchas

- `LANGGRAPH_DEPLOYMENT_URL` is required (no hardcoded fallback in `server.ts`). Missing var throws at startup with a pointed message.
- LangGraph state channels error on >1 write per step unless the field has a reducer. `cart` and `todos` both use `_last_write_wins` so frontend `setState` can coexist with tool-side `Command(update=...)`.
- After calling a cart-mutating tool, the user may click `+`/`−` on the cart card or side panel — those clicks mutate shared state directly without a tool call. Always call `view_cart` before answering cart-related questions; do not trust prior tool args.
- `copilotkit` PyPI pins to Python `<3.13` for older versions — stick to 3.12 unless `requirements.txt` is updated.
