"""LangGraph + CopilotKit agent wiring.

Pure-Python food-delivery domain lives in `food/`; this package wraps those
functions as LangChain @tool decorators, declares the shared state schema,
holds the system prompt, and assembles the agent. `main.py` only
mounts the assembled `agent` on FastAPI — no agent construction lives there.

File map:
  • state.py   — `AgentState`, `Cart`, `CartItem`, `last_write_wins` reducer
  • tools.py   — 11 @tool wrappers + `FOOD_DELIVERY_TOOLS` registration list
  • prompt.py  — `SYSTEM_PROMPT` (intent routing, stop conditions)
  • agent.py   — model selection + `create_agent` + AG-UI wrapper

Key CopilotKit primitives showcased here:

  • `AgentState` — shared state between the agent and the frontend.
    Fields are auto-synced both ways. See `state.py`.

  • `@tool` — registers a Python function as an LLM tool. See `tools.py`.

  • `Command(update={...})` — how a tool *writes* to shared state. The
    cart-mutating tools in `tools.py` use this so `AgentState.cart` updates
    propagate to the frontend automatically.

  • `ToolRuntime` — injected when a tool needs to *read* current state
    (`runtime.state.get(...)`) or grab the current tool_call_id.

  • Controlled-GenUI components registered on the frontend via `useComponent`
    are advertised to the agent as tools automatically by the CopilotKit
    runtime, so the agent can call them by name like any other tool.
"""

from agent.agent import agent, graph
from agent.prompt import SYSTEM_PROMPT
from agent.state import AgentState, Cart, CartItem, last_write_wins
from agent.tools import FOOD_DELIVERY_TOOLS

__all__ = [
    "AgentState",
    "Cart",
    "CartItem",
    "FOOD_DELIVERY_TOOLS",
    "SYSTEM_PROMPT",
    "agent",
    "graph",
    "last_write_wins",
]
