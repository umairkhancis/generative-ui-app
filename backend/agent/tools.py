"""Agent tools — LangChain `@tool` wrappers over the pure `food/` package.

Read-only tools return JSON to the LLM. Cart-mutating tools return a
`Command(update={"cart": ...})` so the new cart lands in shared state and
the React `cartSummaryCard` re-renders automatically.

`FOOD_DELIVERY_TOOLS` at the bottom is the registration list
`main.py` passes to `create_agent`.
"""

from __future__ import annotations

import json
from typing import Any

from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.types import Command

import food as fd


# ── Catalog / search (read-only, return JSON to the agent) ────────────────────

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


# ── Cart (mutate shared state via Command) ────────────────────────────────────
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


# ── Orders ────────────────────────────────────────────────────────────────────

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


# ── Registration list ─────────────────────────────────────────────────────────

FOOD_DELIVERY_TOOLS = [
    # Discovery / search (read-only)
    fetch_nearby_restaurants,
    search_restaurants_by_query,
    fetch_menu_items,
    search_menu_items_by_query,
    # Cart (mutate AgentState.cart via Command)
    add_to_cart,
    update_cart_item,
    remove_cart_item,
    clear_cart,
    view_cart,
    # Orders
    place_order,
    get_order_status,
]
