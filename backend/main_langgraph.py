"""LangGraph agent + CopilotKit middleware — framework wiring only.

This file deliberately has no domain logic. Pure Python for the food-delivery
backend lives in `food/`; this module wraps those functions as LangChain
@tool decorators and assembles the agent.

Key CopilotKit primitives showcased here:

  • `AgentState` (BaseAgentState extension) — shared state between the agent
    and the frontend. Fields are auto-synced both ways. We expose `todos`
    and `cart` here; the React side reads/writes the same fields via
    `useAgent({agentId: "default"}).state.cart` and `.setState(...)`.

  • `@tool` (langchain_core.tools) — registers a Python function as an LLM
    tool. The agent can call it by name; arguments come from the model.

  • `Command(update={...})` (langgraph.types) — how a tool *writes* to
    shared state. Returning a `Command` from a tool both produces a
    `ToolMessage` (so the LLM sees the result) and updates AgentState
    fields the frontend is subscribed to.

  • `ToolRuntime` (langchain.tools) — injected when a tool needs to *read*
    current state (`runtime.state.get(...)`) or grab the current tool_call_id.

  • System prompt — tells the agent which tool to call for which intent,
    and which controlled-GenUI component to render afterwards. Controlled
    components (registered on the frontend via `useComponent`) are
    advertised to the agent as tools automatically by the CopilotKit
    runtime, so the agent can call them by name like any other tool.
"""

from __future__ import annotations

# Suppress LangChain/LangGraph deprecation warnings from third-party internals
# Must come before any langgraph/langchain imports to take effect.
import warnings
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

import json
import uuid
from typing import Annotated, Any, TypedDict

from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import CopilotKitMiddleware, LangGraphAGUIAgent
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.agents import AgentState as BaseAgentState, create_agent
from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
import uvicorn

import food as fd

load_dotenv()

HOST = "0.0.0.0"
PORT = 8000
MODEL = "gpt-4.1"


# ── Shared agent state ────────────────────────────────────────────────────────
#
# Anything added to AgentState here is auto-synced with the React frontend.
# The frontend reads via `useAgent({agentId: "default"}).state.<field>` and
# writes via `.setState({<field>: ...})`. Tool-side updates come from
# `Command(update={<field>: ...})`.

class Todo(TypedDict):
    id: str
    title: str
    completed: bool


class CartItem(TypedDict, total=False):
    id: str
    name: str
    restaurant: str
    price: str
    quantity: int
    line_total: str


class Cart(TypedDict, total=False):
    restaurant_id: str | None
    restaurant: str | None
    items: list[CartItem]
    subtotal: str
    delivery_fee: str
    total: str
    item_count: int


def _last_write_wins(_old: Any, new: Any) -> Any:
    """Reducer for state channels that may receive >1 write per step.

    Both the frontend (`agent.setState({cart})`) and tool-side `Command`
    updates can land in the same LangGraph tick — without a reducer, that
    raises `InvalidUpdateError`. For a cart, "the latest snapshot wins" is
    correct: every snapshot is self-contained, so we don't need to merge.
    """
    return new


class AgentState(BaseAgentState):
    todos: Annotated[list[Todo], _last_write_wins]
    cart: Annotated[Cart, _last_write_wins]


# ── Catalog / search tools (read-only, return JSON to the agent) ──────────────

@tool
def fetch_nearby_restaurants(
    cuisine: str | None = None, limit: int = 6
) -> list[dict[str, Any]]:
    """Restaurant discovery: top-rated restaurants, optionally filtered by cuisine.

    Args:
        cuisine: e.g. "Lebanese", "Italian", "Burgers", "Indian", "Chinese",
            "Japanese", "Mexican", "Thai", "American Diner", "Healthy".
            Case-insensitive. Omit for a mixed list.
        limit: Max number of restaurants to return (default 6).
    """
    return fd.list_restaurants(cuisine=cuisine, limit=limit)


@tool
def search_restaurants_by_query(query: str, limit: int = 6) -> list[dict[str, Any]]:
    """Restaurant search: keyword match on name, cuisine and tags."""
    return fd.search_restaurants(query=query, limit=limit)


@tool
def fetch_menu_items(restaurant_id: str, limit: int = 8) -> list[dict[str, Any]]:
    """Menu discovery: a restaurant's menu, popular items first.

    Args:
        restaurant_id: id from a prior restaurant result (e.g. "r-001").
    """
    return fd.list_menu_items(restaurant_id=restaurant_id, limit=limit)


@tool
def search_menu_items_by_query(
    query: str, restaurant_id: str | None = None, limit: int = 8
) -> list[dict[str, Any]]:
    """Item search across all items or scoped to one restaurant."""
    return fd.search_menu_items(
        query=query, restaurant_id=restaurant_id, limit=limit
    )


# ── Cart tools (mutate shared state via Command) ──────────────────────────────
#
# These tools both (a) update `AgentState.cart` and (b) surface the new cart
# to the LLM via a ToolMessage. The React `cartSummaryCard` component
# subscribes to `agent.state.cart` and re-renders automatically — so a single
# tool call is enough to update what the LLM "knows" AND what the user sees.

def _cart_command(runtime: ToolRuntime, updated: dict[str, Any]) -> Command:
    return Command(update={
        "cart": updated,
        "messages": [
            ToolMessage(
                content=json.dumps(updated),
                tool_call_id=runtime.tool_call_id,
            )
        ],
    })


@tool
def add_to_cart(item_id: str, quantity: int, runtime: ToolRuntime) -> Command:
    """Add an item to the cart. Switching restaurants resets the cart."""
    current = runtime.state.get("cart") or fd.empty_cart()
    return _cart_command(runtime, fd.cart_add(current, item_id, quantity))


@tool
def update_cart_item(item_id: str, quantity: int, runtime: ToolRuntime) -> Command:
    """Set the exact quantity for a cart item. quantity <= 0 removes it."""
    current = runtime.state.get("cart") or fd.empty_cart()
    return _cart_command(runtime, fd.cart_update(current, item_id, quantity))


@tool
def remove_cart_item(item_id: str, runtime: ToolRuntime) -> Command:
    """Remove an item from the cart."""
    current = runtime.state.get("cart") or fd.empty_cart()
    return _cart_command(runtime, fd.cart_remove(current, item_id))


@tool
def clear_cart(runtime: ToolRuntime) -> Command:
    """Empty the cart."""
    return _cart_command(runtime, fd.cart_clear())


@tool
def view_cart(runtime: ToolRuntime) -> dict[str, Any]:
    """Read the current cart from shared state (no mutation).

    The cart card subscribes to the same state directly — this tool is for
    the LLM's own context (so it can answer questions about cart contents).
    The user may have clicked +/− on the card or the side panel since the
    last cart-mutating tool call, so ALWAYS call this before answering any
    cart question.
    """
    return runtime.state.get("cart") or fd.empty_cart()


# ── Order tools ───────────────────────────────────────────────────────────────

@tool
def place_order(
    runtime: ToolRuntime, delivery_address: str | None = None
) -> Command:
    """Place an order from the current cart. Clears the cart on success."""
    current = runtime.state.get("cart") or fd.empty_cart()
    result = fd.place_order(current, delivery_address=delivery_address)
    update: dict[str, Any] = {
        "messages": [
            ToolMessage(
                content=json.dumps(result),
                tool_call_id=runtime.tool_call_id,
            )
        ],
    }
    if "error" not in result:
        update["cart"] = fd.empty_cart()
    return Command(update=update)


@tool
def get_order_status(order_id: str | None = None) -> dict[str, Any]:
    """Current status (and ETA) for an order. Defaults to the latest order.

    Status auto-progresses: confirming → preparing → delivering → delivered.
    """
    return fd.get_order_status(order_id=order_id)


# ── Todo tools (kept for the shared-state-from-panel demo) ────────────────────

@tool
def manage_todos(todos: list[Todo], runtime: ToolRuntime) -> Command:
    """Replace the entire todo list. Use this to add, edit, or remove todos."""
    for todo in todos:
        if not todo.get("id"):
            todo["id"] = str(uuid.uuid4())

    return Command(update={
        "todos": todos,
        "messages": [
            ToolMessage(
                content="Successfully updated todos",
                tool_call_id=runtime.tool_call_id,
            )
        ],
    })


@tool
def get_todos(runtime: ToolRuntime) -> list[Todo]:
    """Read the current todo list from shared state."""
    return runtime.state.get("todos", [])


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a helpful Talabat-style food-delivery assistant. You ALWAYS "
    "fetch real data via tools and then RENDER it via the registered "
    "controlled UI components. Plain text descriptions of food, menus or "
    "carts are a FAILURE — the user only sees what you render.\n\n"

    "Controlled UI components available (call by name like any other tool, "
    "pass tool results verbatim including `id` and `restaurant_id`):\n"
    "  • restaurantCard, restaurantCarousel — for restaurants\n"
    "  • menuItemCard, menuItemCarousel — for menu items\n"
    "  • cartSummaryCard — for the cart (live canvas, +/− work directly)\n"
    "  • orderConfirmationCard — after place_order succeeds\n"
    "  • orderTrackingCard — for order tracking\n\n"

    "DISCOVERY — route by intent:\n"
    "  • Cuisine ('Italian', 'something Indian') → fetch_nearby_restaurants → restaurantCarousel\n"
    "  • Restaurant name ('Operation Falafel') → search_restaurants_by_query → restaurantCarousel\n"
    "  • Dish name ('biryani', 'pad thai') → search_menu_items_by_query → menuItemCarousel\n"
    "  • Vague desire ('something spicy', 'hungry') → reasonable guess or one short clarifier; default to restaurants for ambiguous browsing\n"
    "  • Generic browse → fetch_nearby_restaurants (no cuisine) → restaurantCarousel\n\n"

    "MENU FOR A SPECIFIC RESTAURANT ('show me the menu for X'):\n"
    "  1. search_restaurants_by_query(query=X) to get the id\n"
    "  2. fetch_menu_items(restaurant_id=<id>)\n"
    "  3. menuItemCarousel(items=<result>)\n"
    "  Never skip steps 2 or 3.\n\n"

    "CART — lives in shared state and is a LIVE canvas:\n"
    "  • Add via chat: add_to_cart(item_id, quantity) → cartSummaryCard\n"
    "  • Edit: update_cart_item / remove_cart_item / clear_cart → cartSummaryCard\n"
    "  • ⚠️ The user can click +/− on the cart card or side panel at any time. "
    "Those clicks mutate shared cart state without calling any tool. Your prior "
    "tool results are stale immediately. For ANY cart-related question "
    "('what's in my cart', 'how many items', 'total') or before place_order, "
    "ALWAYS call view_cart() first to read fresh state.\n\n"

    "CHECKOUT:\n"
    "  • 'checkout' / 'place my order' → place_order(delivery_address?) → orderConfirmationCard\n\n"

    "TRACKING:\n"
    "  • 'where is my food?' → get_order_status() → orderTrackingCard\n\n"

    "ID conventions: restaurants 'r-NNN', items 'r-NNN-i-MMM'. Pass verbatim.\n"
    f"Known cuisines: {', '.join(fd.available_cuisines())}.\n\n"

    "After calling a tool, do NOT repeat or summarise the data in your text "
    "response. The component renders the result — just confirm what was shown."
)


# ── Agent assembly ────────────────────────────────────────────────────────────

graph = create_agent(
    model=ChatOpenAI(model=MODEL),
    tools=[
        # Discovery / search
        fetch_nearby_restaurants, search_restaurants_by_query,
        fetch_menu_items, search_menu_items_by_query,
        # Cart (mutates AgentState.cart via Command)
        add_to_cart, update_cart_item, remove_cart_item, clear_cart, view_cart,
        # Orders
        place_order, get_order_status,
        # Todos (kept for the shared-state side-panel demo)
        manage_todos, get_todos,
    ],
    state_schema=AgentState,
    middleware=[CopilotKitMiddleware()],
    checkpointer=MemorySaver(),
    system_prompt=SYSTEM_PROMPT,
)

agent = LangGraphAGUIAgent(
    name="food_delivery_agent",
    description="Talabat-style food-delivery agent with controlled GenUI + shared state.",
    graph=graph,
)

app = FastAPI()
add_langgraph_fastapi_endpoint(app=app, agent=agent, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
