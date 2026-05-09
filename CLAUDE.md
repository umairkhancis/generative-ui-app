# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Three runtimes, four ports — the system is intentionally split:

```
Browser → Vite (5173)
            └── proxy /api/copilotkit → CopilotKit runtime (4002, Node/Hono)
                                          ├── agentId "default" → LangGraph backend (8000, Python/FastAPI)
                                          └── agentId "gemini"  → ADK backend       (8009, Python/FastAPI)
```

- **`backend/main_adk.py`** (`:8009`) — Google ADK `LlmAgent` + Gemini, exposed via `add_adk_fastapi_endpoint(path="/")`.
- **`backend/main_langgraph.py`** (`:8000`) — LangChain `create_agent` (OpenAI `gpt-4.1`) wrapped with `CopilotKitMiddleware` and a `MemorySaver` checkpointer, exposed via `add_langgraph_fastapi_endpoint(path="/")`. Both Python apps mount at `path="/"`, which is why they must run on separate ports.
- **`frontend/server.ts`** — defines a `CopilotRuntime` whose `agents` map binds the two `agentId`s to the two Python URLs. Run by `frontend/watch-server.ts`, which `fork`s `server.ts` under `tsx/esm` and restarts it on file change.
- **`frontend/src/App.tsx`** — `agentId` constant (`"default"` or `"gemini"`) picks which Python backend the chat hits. This is the toggle for switching agent providers.
- **`frontend/vite.config.ts`** — proxies `/api/copilotkit` → `localhost:4002` so the React app talks to the Node runtime, never directly to Python.

URLs are overridable via env: `LANGGRAPH_DEPLOYMENT_URL`, `ADK_AGENT_URL`.

`backend/helper.py` is a notebook utility module (API-key loaders, port helpers, etc.) — not imported by the FastAPI servers themselves.

## Commands

### Backend (Python 3.12 — copilotkit + ag-ui-adk both require ≥3.10)

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # then fill OPENAI_API_KEY + GOOGLE_API_KEY

.venv/bin/python main_adk.py        # ADK on :8009
.venv/bin/python main_langgraph.py  # LangGraph on :8000
```

Run both — the frontend expects them to be reachable independently.

### Frontend

```bash
cd frontend
npm install
npm run dev      # starts watch-server.ts (runtime on :4002) AND vite (:5173)
npm run build    # vite production build
npm run preview  # serve the build
npm run test:e2e # playwright (testDir ./e2e — currently empty)
```

`npm run dev` launches the Node runtime and Vite together (`node --import tsx/esm watch-server.ts & vite`); you don't need a separate process for `server.ts`.

### Restarting the whole stack

```bash
# kill any leftovers
for p in 8000 8009 4002 5173; do kill -9 $(lsof -ti:$p) 2>/dev/null; done
# then start the three commands above in separate terminals
```

## Gotchas

- The `agentId` in `App.tsx` must match a key in the `agents` map in `server.ts` — adding a new backend means editing both.
- `backend/.env` is loaded by `load_dotenv()` at the top of each `main_*.py`. The notebook-style fallback to `helper.get_openai_api_key()` was removed during refactor; the `.env` is the only source.
- `copilotkit` PyPI package pins to Python `<3.13` for older versions — stick to 3.12 unless requirements.txt is updated.
