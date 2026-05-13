"""Talabat-style mock food-delivery backend (pure Python — no framework deps).

The package is split by concern so each file is small and focused:

    catalog.py — CSV-backed restaurant & menu queries (read-only)
    cart.py    — pure cart operations (every fn returns a new cart snapshot)
    orders.py  — order placement & time-progressed status tracking

Nothing in this package imports LangGraph / CopilotKit. The framework
adapter (`main_langgraph.py`) imports these functions and wraps them in
`@tool` decorators.

CSV files live under `food/db/`.
"""

from food.catalog import (  # noqa: F401
    available_cuisines,
    list_menu_items,
    list_restaurants,
    search_menu_items,
    search_restaurants,
)
from food.cart import (  # noqa: F401
    cart_add,
    cart_clear,
    cart_remove,
    cart_update,
    empty_cart,
)
from food.orders import (  # noqa: F401
    get_order_status,
    place_order,
)
