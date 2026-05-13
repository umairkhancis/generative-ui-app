from __future__ import annotations

# Suppress LangChain/LangGraph deprecation warnings from third-party internals
# Must come before any langgraph/langchain imports to take effect.
import warnings
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

# ── Standard library ──────────────────────────────────────────────────────────
import csv
import json
import os
import uuid
from pathlib import Path
from typing import Any, TypedDict

# ── LangChain / LangGraph ─────────────────────────────────────────────────────
from langchain.agents import AgentState as BaseAgentState, create_agent
from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# ── CopilotKit ────────────────────────────────────────────────────────────────
from copilotkit import CopilotKitMiddleware, LangGraphAGUIAgent, a2ui
from ag_ui_langgraph import add_langgraph_fastapi_endpoint

# ── Food-delivery backend ─────────────────────────────────────────────────────
import food_data as fd

# ── Web framework ─────────────────────────────────────────────────────────────
from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

load_dotenv()

HOST = "0.0.0.0"
PORT = 8000
MODEL = "gpt-4.1"
# optional — omit to use OpenAI directly
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL")

SYSTEM_PROMPT = (
    "You are a helpful assistant that creates rich visual UI.\n\n"
    "Tool guidance:\n"
    "- ALL flight-related queries: first call search_flights to fetch flight "
    "data, then call display_flights with the results. NEVER use generate_a2ui "
    "for flights.\n"
    "- For sales/business data requests: first call get_sales_data to fetch "
    "the latest metrics, then call generate_a2ui to visualize the results.\n"
    "- For other rich UI: call generate_a2ui directly.\n\n"
    "Food-delivery guidance (Talabat-style ordering journey):\n"
    "Always FETCH from the backend tools first, then RENDER with the matching "
    "controlled component. Never invent restaurant, menu, cart or order data.\n"
    "1. RESTAURANT DISCOVERY — show restaurants nearby / by cuisine:\n"
    "   → call `fetch_nearby_restaurants(cuisine?, limit?)`\n"
    "   → render `restaurantCarousel({ restaurants: <result> })` "
    "(or `restaurantCard` if exactly one).\n"
    "2. RESTAURANT SEARCH — find a specific place by keyword:\n"
    "   → call `search_restaurants_by_query(query, limit?)`\n"
    "   → render `restaurantCarousel`.\n"
    "3. MENU DISCOVERY — show a restaurant's menu:\n"
    "   → call `fetch_menu_items(restaurant_id, limit?)` using the `id` from a "
    "prior restaurant result\n"
    "   → render `menuItemCarousel({ items: <result> })`.\n"
    "4. ITEM SEARCH — find specific dishes:\n"
    "   → call `search_menu_items_by_query(query, restaurant_id?, limit?)`\n"
    "   → render `menuItemCarousel`.\n"
    "5. ADD TO CART — user says 'add X to cart' / 'order N of Y':\n"
    "   → call `add_to_cart(item_id, quantity?)` using item ids from prior "
    "menu results. Then render `cartSummaryCard` with the returned snapshot.\n"
    "6. EDIT CART — change quantity / remove / clear:\n"
    "   → call `update_cart_item(item_id, quantity)`, `remove_cart_item`, or "
    "`clear_cart`. Render `cartSummaryCard`.\n"
    "7. VIEW CART — 'show my cart' / 'what's in my order':\n"
    "   → call `view_cart()` → render `cartSummaryCard`.\n"
    "8. PLACE ORDER — 'checkout' / 'place order' / 'confirm order':\n"
    "   → call `place_order(delivery_address?)` → render "
    "`orderConfirmationCard` with the returned data.\n"
    "9. TRACK ORDER — 'where is my food' / 'track my order':\n"
    "   → call `get_order_status(order_id?)` → render `orderTrackingCard` "
    "with the returned data. Status auto-progresses with time.\n"
    "ID conventions: restaurant ids look like 'r-001', item ids 'r-001-i-007'. "
    "Pass them back verbatim — do not modify or invent.\n"
    f"Known cuisines: {', '.join(fd.available_cuisines())}.\n\n"
    "Airline logos: use https://www.gstatic.com/flights/airline_logos/70px/<IATA>.png\n"
    "Common codes: DL=Delta, UA=United, AA=American, WN=Southwest, B6=JetBlue, "
    "NK=Spirit, AS=Alaska, F9=Frontier, BA=British Airways, LH=Lufthansa, "
    "AF=Air France, EK=Emirates, QF=Qantas, SQ=Singapore Airlines, NH=ANA.\n\n"
    "IMPORTANT: After calling a tool, do NOT repeat or summarize the data "
    "in your text response. The tool renders UI automatically. "
    "Just confirm what was rendered."
)

CSV_PATH = Path(__file__).resolve().parent / "data" / "db.csv"


# ── Todo state ────────────────────────────────────────────────────────────────

class Todo(TypedDict):
    id: str
    title: str
    completed: bool


class AgentState(BaseAgentState):
    todos: list[Todo]

# ── Tools ─────────────────────────────────────────────────────────────────────


@tool
def query_data(query: str) -> list[dict[str, Any]]:
    """Query the lesson dataset. Always call before showing a chart or graph."""
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


@tool
def get_sales_data() -> str:
    """Fetch current sales metrics and revenue data.

    Returns sales data including revenue, customers, conversion rates,
    and breakdowns by category and month.
    """
    return json.dumps({
        "totalRevenue": "$1.2M",
        "newCustomers": 3842,
        "conversionRate": "3.6%",
        "revenueByCategory": [
            {"label": "Electronics", "value": 420000},
            {"label": "Clothing", "value": 310000},
            {"label": "Home & Garden", "value": 185000},
            {"label": "Sports", "value": 160000},
            {"label": "Books", "value": 125000},
        ],
        "monthlySales": [
            {"label": "Jan", "value": 85000},
            {"label": "Feb", "value": 92000},
            {"label": "Mar", "value": 108000},
            {"label": "Apr", "value": 95000},
            {"label": "May", "value": 115000},
            {"label": "Jun", "value": 125000},
        ],
    })


# ── Flight tools ──────────────────────────────────────────────────────────────

CATALOG_ID = "copilotkit://app-dashboard-catalog"
SURFACE_ID = "flight-search-results"

FLIGHT_SCHEMA = [
    {"id": "root", "component": "List", "children": {"componentId": "flight-card",
                                                     "path": "/flights"}, "direction": "horizontal", "gap": 16},
    {"id": "flight-card", "component": "Card", "child": "main-col"},
    {"id": "main-col", "component": "Column", "children": ["airline-img", "header-row", "meta-row", "divider-1",
                                                           "times-row", "route-row", "divider-2", "status-row", "divider-3", "book-btn"], "align": "stretch", "gap": 8},
    {"id": "airline-img", "component": "Image", "src": {"path": "airlineLogo"},
        "alt": {"path": "airline"}, "height": 32},
    {"id": "header-row", "component": "Row",
        "children": ["airline-name", "price-text"], "justify": "spaceBetween", "align": "center"},
    {"id": "airline-name", "component": "Text",
        "text": {"path": "airline"}, "variant": "h3"},
    {"id": "price-text", "component": "Text",
        "text": {"path": "price"}, "variant": "h2"},
    {"id": "meta-row", "component": "Row",
        "children": ["flight-number", "date-text"], "justify": "spaceBetween", "align": "center"},
    {"id": "flight-number", "component": "Text",
        "text": {"path": "flightNumber"}, "variant": "caption"},
    {"id": "date-text", "component": "Text",
        "text": {"path": "date"}, "variant": "caption"},
    {"id": "divider-1", "component": "Divider"},
    {"id": "times-row", "component": "Row",
        "children": ["depart-time", "duration-text", "arrive-time"], "justify": "spaceBetween", "align": "center"},
    {"id": "depart-time", "component": "Text",
        "text": {"path": "departureTime"}, "variant": "h2"},
    {"id": "duration-text", "component": "Text",
        "text": {"path": "duration"}, "variant": "caption"},
    {"id": "arrive-time", "component": "Text",
        "text": {"path": "arrivalTime"}, "variant": "h2"},
    {"id": "route-row", "component": "Row",
        "children": ["origin-code", "arrow-text", "dest-code"], "justify": "spaceBetween", "align": "center"},
    {"id": "origin-code", "component": "Text",
        "text": {"path": "origin"}, "variant": "h3"},
    {"id": "arrow-text", "component": "Text", "text": "→", "variant": "h3"},
    {"id": "dest-code", "component": "Text",
        "text": {"path": "destination"}, "variant": "h3"},
    {"id": "divider-2", "component": "Divider"},
    {"id": "status-row", "component": "Row",
        "children": ["status-text"], "align": "center"},
    {"id": "status-text", "component": "Text",
        "text": {"path": "status"}, "variant": "caption"},
    {"id": "divider-3", "component": "Divider"},
    {"id": "book-btn", "component": "Button", "label": "Book Flight",
        "variant": "primary", "action": {"event": {"name": "bookFlight"}}},
]


class Flight(TypedDict):
    id: str
    airline: str
    airlineLogo: str
    flightNumber: str
    origin: str
    destination: str
    date: str
    departureTime: str
    arrivalTime: str
    duration: str
    status: str
    price: str


@tool
def search_flights(origin: str, destination: str) -> list[Flight]:
    """Search for available flights between two airports.

    Args:
        origin: Origin airport IATA code (e.g. "SFO").
        destination: Destination airport IATA code (e.g. "JFK").
    """
    return [
        {"id": "1", "airline": "Delta Air Lines", "airlineLogo": "https://www.gstatic.com/flights/airline_logos/70px/DL.png", "flightNumber": "DL 520", "origin": origin,
            "destination": destination, "date": "2026-04-11", "departureTime": "08:00", "arrivalTime": "16:35", "duration": "5h 35m", "status": "On Time", "price": "$389"},
        {"id": "2", "airline": "United Airlines", "airlineLogo": "https://www.gstatic.com/flights/airline_logos/70px/UA.png", "flightNumber": "UA 1583", "origin": origin,
            "destination": destination, "date": "2026-04-11", "departureTime": "10:15", "arrivalTime": "18:42", "duration": "5h 27m", "status": "On Time", "price": "$412"},
        {"id": "3", "airline": "JetBlue", "airlineLogo": "https://www.gstatic.com/flights/airline_logos/70px/B6.png", "flightNumber": "B6 416", "origin": origin,
            "destination": destination, "date": "2026-04-11", "departureTime": "14:30", "arrivalTime": "23:05", "duration": "5h 35m", "status": "On Time", "price": "$345"},
        {"id": "4", "airline": "American Airlines", "airlineLogo": "https://www.gstatic.com/flights/airline_logos/70px/AA.png", "flightNumber": "AA 178", "origin": origin,
            "destination": destination, "date": "2026-04-11", "departureTime": "17:00", "arrivalTime": "01:20+1", "duration": "5h 20m", "status": "On Time", "price": "$398"},
    ]


@tool
def display_flights(flights: list[Flight]) -> str:
    """Display flights as rich cards in a horizontal row.

    Each flight must have: id, airline, airlineLogo (URL), flightNumber,
    origin, destination, date, departureTime, arrivalTime, duration,
    status, and price.
    """
    return a2ui.render(
        operations=[
            a2ui.create_surface(SURFACE_ID, catalog_id=CATALOG_ID),
            a2ui.update_components(SURFACE_ID, FLIGHT_SCHEMA),
            a2ui.update_data_model(SURFACE_ID, {"flights": flights}),
        ],
    )


# ── Food-delivery tools ───────────────────────────────────────────────────────


@tool
def fetch_nearby_restaurants(
    cuisine: str | None = None, limit: int = 6
) -> list[dict[str, Any]]:
    """Restaurant discovery: fetch curated nearby restaurants, top-rated first.

    Args:
        cuisine: Optional cuisine filter (e.g. "Lebanese", "Italian", "Burgers",
            "Indian", "Chinese", "Japanese", "Mexican", "Thai",
            "American Diner", "Healthy"). Case-insensitive. Omit for mixed.
        limit: Max number of restaurants to return (default 6).

    Each restaurant: id, name, cuisine, rating, delivery_time, delivery_fee, tags.
    """
    return fd.list_restaurants(cuisine=cuisine, limit=limit)


@tool
def search_restaurants_by_query(query: str, limit: int = 6) -> list[dict[str, Any]]:
    """Restaurant search: keyword search on name, cuisine and tags."""
    return fd.search_restaurants(query=query, limit=limit)


@tool
def fetch_menu_items(restaurant_id: str, limit: int = 8) -> list[dict[str, Any]]:
    """Menu discovery: fetch a restaurant's menu, popular items first.

    Args:
        restaurant_id: Restaurant id from a prior restaurant result (e.g. "r-001").
        limit: Max number of items to return (default 8).

    Each item: id, restaurant_id, restaurant, name, description, price, spicy,
    vegetarian, popular.
    """
    return fd.list_menu_items(restaurant_id=restaurant_id, limit=limit)


@tool
def search_menu_items_by_query(
    query: str, restaurant_id: str | None = None, limit: int = 8
) -> list[dict[str, Any]]:
    """Item search: keyword search across all items or scoped to one restaurant."""
    return fd.search_menu_items(
        query=query, restaurant_id=restaurant_id, limit=limit
    )


@tool
def add_to_cart(item_id: str, quantity: int = 1) -> dict[str, Any]:
    """Add an item to the cart. Returns the updated cart snapshot.

    Adding from a different restaurant than the current cart's resets the cart.
    """
    return fd.add_to_cart(item_id=item_id, quantity=quantity)


@tool
def update_cart_item(item_id: str, quantity: int) -> dict[str, Any]:
    """Set the exact quantity for a cart item. quantity <= 0 removes it."""
    return fd.update_cart_item(item_id=item_id, quantity=quantity)


@tool
def remove_cart_item(item_id: str) -> dict[str, Any]:
    """Remove an item from the cart."""
    return fd.remove_from_cart(item_id=item_id)


@tool
def clear_cart() -> dict[str, Any]:
    """Empty the cart."""
    return fd.clear_cart()


@tool
def view_cart() -> dict[str, Any]:
    """Return the current cart snapshot: items, subtotal, delivery_fee, total."""
    return fd.view_cart()


@tool
def place_order(delivery_address: str | None = None) -> dict[str, Any]:
    """Place an order from the current cart. Clears the cart on success.

    Returns: order_id, restaurant, items, totals, status ('confirming'), eta.
    """
    return fd.place_order(delivery_address=delivery_address)


@tool
def get_order_status(order_id: str | None = None) -> dict[str, Any]:
    """Get current status of an order (defaults to the latest order).

    Status progresses with time: confirming → preparing → delivering → delivered.
    """
    return fd.get_order_status(order_id=order_id)


# ── Todo tools ────────────────────────────────────────────────────────────────

@tool
def manage_todos(todos: list[Todo], runtime: ToolRuntime) -> Command:
    """Replace the entire todo list. Use this to add, edit, or remove todos."""
    for todo in todos:
        if not todo.get("id"):
            todo["id"] = str(uuid.uuid4())

    # Command allows agents to update state via toolcalls
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
def get_todos(runtime: ToolRuntime):
    """Get the current todo list."""
    return runtime.state.get("todos", [])


# ── Agent & app ───────────────────────────────────────────────────────────────

graph = create_agent(
    model=ChatOpenAI(
        model=MODEL, **({"base_url": LITELLM_BASE_URL} if LITELLM_BASE_URL else {})),
    tools=[query_data, get_sales_data, search_flights,
           display_flights, manage_todos, get_todos,
           fetch_nearby_restaurants, search_restaurants_by_query,
           fetch_menu_items, search_menu_items_by_query,
           add_to_cart, update_cart_item, remove_cart_item, clear_cart,
           view_cart, place_order, get_order_status],
    state_schema=AgentState,
    middleware=[CopilotKitMiddleware()],
    checkpointer=MemorySaver(),
    system_prompt=SYSTEM_PROMPT,
)

agent = LangGraphAGUIAgent(
    name="lesson2_agent",
    description="Lesson 2 chart agent",
    graph=graph,
)

app = FastAPI()
add_langgraph_fastapi_endpoint(app=app, agent=agent, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
