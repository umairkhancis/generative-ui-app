"""Build the LangGraph agent and wrap it for AG-UI streaming.

Pulls the pieces from this package's other modules:
  • `state.AgentState`           — shared-state schema (auto-synced with React)
  • `tools.FOOD_DELIVERY_TOOLS`  — the 11 @tool wrappers around `food/`
  • `prompt.SYSTEM_PROMPT`       — journey playbook for the LLM

Model: OpenAI `gpt-4.1` by default. Set `LITELLM_BASE_URL` in
`backend/.env` to route through a LiteLLM proxy instead (useful for local
proxies, custom routing, or non-OpenAI providers exposed via LiteLLM).

Recursion ceiling is bumped to 60 — the default 25 is too tight for a
multi-step journey (search → fetch menu → render → add → render →
checkout → place_order → render).

Exports:
  • `graph` — the compiled LangGraph (rarely needed externally)
  • `agent` — `LangGraphAGUIAgent` ready to mount on FastAPI
"""

from __future__ import annotations

import os

from copilotkit import CopilotKitMiddleware, LangGraphAGUIAgent
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from agent.prompt import SYSTEM_PROMPT
from agent.state import AgentState
from agent.tools import FOOD_DELIVERY_TOOLS

load_dotenv()

MODEL = "gpt-4.1"
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL")
RECURSION_LIMIT = 60


graph = create_agent(
    model=ChatOpenAI(
        model=MODEL,
        **({"base_url": LITELLM_BASE_URL} if LITELLM_BASE_URL else {}),
    ),
    tools=FOOD_DELIVERY_TOOLS,
    state_schema=AgentState,
    middleware=[CopilotKitMiddleware()],
    checkpointer=MemorySaver(),
    system_prompt=SYSTEM_PROMPT,
).with_config({"recursion_limit": RECURSION_LIMIT})


agent = LangGraphAGUIAgent(
    name="food_delivery_agent",
    description="Talabat-style food-delivery agent with controlled GenUI + shared state.",
    graph=graph,
)
