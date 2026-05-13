"""FastAPI ↔ agent integration.

Mounts the assembled `agent` (from the `agent/` package) on `/`, then runs
uvicorn. The agent itself — model, tools, state, prompt, graph — is built
inside `agent/`; this file holds zero agent construction.

Run directly (`python main.py`) or via `make up-langgraph`.
"""

from __future__ import annotations

# Suppress LangChain/LangGraph deprecation warnings from third-party internals.
# Must come BEFORE the `agent` import, which triggers langgraph imports.
import warnings
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from fastapi import FastAPI
import uvicorn

from agent import agent

app = FastAPI()

# Mount the AG-UI streaming endpoint so the Node runtime can talk to the agent.
add_langgraph_fastapi_endpoint(app=app, agent=agent, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
