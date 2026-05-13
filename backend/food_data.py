"""Talabat-style mock food-delivery backend.

CSV-backed catalogue plus in-memory cart and order state. Drives the full
ordering journey: discovery → search → menu → cart → checkout → tracking.

Storage:
    backend/data/restaurants.csv   — seeded by `_seed_food_data.py`
    backend/data/menu_items.csv    — seeded by `_seed_food_data.py`

Runtime (in-memory, single-conversation): a singleton cart and an order log.

Public API — each function maps to one agent tool in `main_langgraph.py`:
    list_restaurants(cuisine=None, limit=12)
    search_restaurants(query, limit=6)
    list_menu_items(restaurant_id, limit=12)
    search_menu_items(query, restaurant_id=None, limit=8)
    add_to_cart(item_id, quantity=1)
    update_cart_item(item_id, quantity)
    remove_from_cart(item_id)
    clear_cart()
    view_cart()
    place_order(delivery_address=None)
    get_order_status(order_id=None)
    available_cuisines()
"""

from __future__ import annotations

import csv
import re
import time
import uuid
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).resolve().parent / "data"
_RESTAURANTS_CSV = _DATA_DIR / "restaurants.csv"
_MENU_ITEMS_CSV = _DATA_DIR / "menu_items.csv"


# ── CSV load ──────────────────────────────────────────────────────────────────

def _load_restaurants() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with _RESTAURANTS_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "id": r["id"],
                "name": r["name"],
                "cuisine": r["cuisine"],
                "rating": float(r["rating"]),
                "delivery_time": r["delivery_time"],
                "delivery_fee": r["delivery_fee"],
                "tags": [t for t in r["tags"].split("|") if t],
            })
    return rows


def _load_menu_items() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with _MENU_ITEMS_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "id": r["id"],
                "restaurant_id": r["restaurant_id"],
                "restaurant": r["restaurant"],
                "name": r["name"],
                "description": r["description"],
                "price": r["price"],
                "spicy": r["spicy"] == "true",
                "vegetarian": r["vegetarian"] == "true",
                "popular": r["popular"] == "true",
            })
    return rows


_RESTAURANTS = _load_restaurants()
_MENU = _load_menu_items()
_RESTAURANT_INDEX = {r["id"]: r for r in _RESTAURANTS}
_ITEM_INDEX = {i["id"]: i for i in _MENU}
_MENU_BY_RESTAURANT: dict[str, list[dict[str, Any]]] = {}
for _it in _MENU:
    _MENU_BY_RESTAURANT.setdefault(_it["restaurant_id"], []).append(_it)


# ── Restaurant queries ────────────────────────────────────────────────────────

def list_restaurants(cuisine: str | None = None, limit: int = 12) -> list[dict[str, Any]]:
    """Discovery: return curated restaurants, optionally filtered by cuisine."""
    pool = _RESTAURANTS
    if cuisine:
        needle = cuisine.strip().lower()
        pool = [r for r in pool if r["cuisine"].lower() == needle]
    # Sort by rating desc so 'top-rated' queries return best first.
    pool = sorted(pool, key=lambda r: -r["rating"])
    return pool[: max(0, limit)]


def search_restaurants(query: str, limit: int = 6) -> list[dict[str, Any]]:
    """Search restaurants by name / cuisine / tag substring."""
    needle = (query or "").strip().lower()
    if not needle:
        return []
    scored: list[tuple[int, dict[str, Any]]] = []
    for r in _RESTAURANTS:
        hay = f"{r['name']} {r['cuisine']} {' '.join(r['tags'])}".lower()
        if needle not in hay:
            continue
        score = 0
        if needle in r["name"].lower():
            score += 10
        if needle == r["cuisine"].lower():
            score += 5
        elif needle in r["cuisine"].lower():
            score += 2
        for t in r["tags"]:
            if needle in t.lower():
                score += 1
        scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], -x[1]["rating"]))
    return [r for _, r in scored[: max(0, limit)]]


def available_cuisines() -> list[str]:
    return sorted({r["cuisine"] for r in _RESTAURANTS})


# ── Menu queries ──────────────────────────────────────────────────────────────

def list_menu_items(restaurant_id: str, limit: int = 12) -> list[dict[str, Any]]:
    """Menu discovery: popular items first, then alphabetical."""
    pool = _MENU_BY_RESTAURANT.get(restaurant_id, [])
    pool = sorted(pool, key=lambda i: (not i["popular"], i["name"]))
    return pool[: max(0, limit)]


def search_menu_items(
    query: str,
    restaurant_id: str | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Item search by name/description, optionally scoped to a restaurant."""
    needle = (query or "").strip().lower()
    if not needle:
        return []
    pool = (
        _MENU_BY_RESTAURANT.get(restaurant_id, [])
        if restaurant_id else _MENU
    )
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in pool:
        hay = f"{item['name']} {item['description']}".lower()
        if needle not in hay:
            continue
        score = 0
        if needle in item["name"].lower():
            score += 10
        if item["popular"]:
            score += 2
        scored.append((score, item))
    scored.sort(key=lambda x: -x[0])
    return [i for _, i in scored[: max(0, limit)]]


# ── Cart helpers (pure functions over a cart snapshot) ────────────────────────
#
# Cart state lives in LangGraph AgentState (so it's shared between the agent
# and the frontend canvas card). These functions are pure: they take the
# current cart snapshot and return a new one. No module globals.

_PRICE_RE = re.compile(r"AED\s*(\d+(?:\.\d+)?)", re.IGNORECASE)


def _parse_price(s: str) -> float:
    if not s:
        return 0.0
    m = _PRICE_RE.search(s)
    return float(m.group(1)) if m else 0.0


def _compute_snapshot(
    quantities: dict[str, int], restaurant_id: str | None
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    subtotal = 0.0
    for iid, qty in quantities.items():
        if qty <= 0:
            continue
        item = _ITEM_INDEX.get(iid)
        if not item:
            continue
        unit = _parse_price(item["price"])
        line = unit * qty
        subtotal += line
        items.append({
            "id": iid,
            "name": item["name"],
            "restaurant": item["restaurant"],
            "price": item["price"],
            "quantity": qty,
            "line_total": f"AED {line:.0f}",
        })
    restaurant = _RESTAURANT_INDEX.get(restaurant_id) if restaurant_id else None
    delivery_fee_val = _parse_price(restaurant["delivery_fee"]) if restaurant else 0.0
    total = subtotal + delivery_fee_val
    return {
        "restaurant_id": restaurant_id if restaurant else None,
        "restaurant": restaurant["name"] if restaurant else None,
        "items": items,
        "subtotal": f"AED {subtotal:.0f}",
        "delivery_fee": restaurant["delivery_fee"] if restaurant else "Free",
        "total": f"AED {total:.0f}",
        "item_count": sum(q for q in quantities.values() if q > 0),
    }


def _quantities_from_cart(cart: dict[str, Any] | None) -> tuple[dict[str, int], str | None]:
    if not cart:
        return {}, None
    quantities = {i["id"]: int(i.get("quantity") or 0) for i in cart.get("items", []) or []}
    return quantities, cart.get("restaurant_id")


def empty_cart() -> dict[str, Any]:
    return _compute_snapshot({}, None)


def cart_add(cart: dict[str, Any] | None, item_id: str, quantity: int = 1) -> dict[str, Any]:
    item = _ITEM_INDEX.get(item_id)
    if not item:
        return cart or empty_cart()
    qty = max(1, int(quantity))
    quantities, rid = _quantities_from_cart(cart)
    if rid is None:
        rid = item["restaurant_id"]
    elif rid != item["restaurant_id"]:
        # Switching restaurants resets the cart.
        quantities = {}
        rid = item["restaurant_id"]
    quantities[item_id] = quantities.get(item_id, 0) + qty
    return _compute_snapshot(quantities, rid)


def cart_update(cart: dict[str, Any] | None, item_id: str, quantity: int) -> dict[str, Any]:
    quantities, rid = _quantities_from_cart(cart)
    if quantity <= 0:
        quantities.pop(item_id, None)
    else:
        item = _ITEM_INDEX.get(item_id)
        if not item:
            return cart or empty_cart()
        if rid is None:
            rid = item["restaurant_id"]
        elif rid != item["restaurant_id"]:
            quantities = {}
            rid = item["restaurant_id"]
        quantities[item_id] = int(quantity)
    if not quantities:
        rid = None
    return _compute_snapshot(quantities, rid)


def cart_remove(cart: dict[str, Any] | None, item_id: str) -> dict[str, Any]:
    return cart_update(cart, item_id, 0)


def cart_clear() -> dict[str, Any]:
    return empty_cart()


# ── Order state & tracking ────────────────────────────────────────────────────

_orders: dict[str, dict[str, Any]] = {}
_latest_order_id: str | None = None

# Compressed for demo: ~3 min total lifecycle.
#   0-30s  : confirming
#   30-90s : preparing
#   90-180s: delivering
#   180s+  : delivered
_STATUS_BUCKETS: list[tuple[float, str]] = [
    (30.0, "confirming"),
    (90.0, "preparing"),
    (180.0, "delivering"),
]


def _derive_status(placed_at: float) -> tuple[str, str]:
    elapsed = time.time() - placed_at
    for upper, status in _STATUS_BUCKETS:
        if elapsed <= upper:
            remaining = 180.0 - elapsed
            if remaining > 60:
                eta = f"{int(remaining // 60)} min"
            elif remaining > 0:
                eta = f"{max(1, int(remaining))} sec"
            else:
                eta = "Arriving"
            return status, eta
    return "delivered", "Arrived"


def place_order(
    cart: dict[str, Any] | None, delivery_address: str | None = None
) -> dict[str, Any]:
    """Convert the given cart snapshot into an order. Caller must clear the cart."""
    global _latest_order_id
    snap = cart or empty_cart()
    if not snap.get("items"):
        return {"error": "Cart is empty. Add items before placing an order."}
    oid = f"TLB-{uuid.uuid4().hex[:4].upper()}"
    order = {
        "order_id": oid,
        "restaurant_id": snap["restaurant_id"],
        "restaurant": snap["restaurant"],
        "items": [
            {"name": i["name"], "quantity": i["quantity"]}
            for i in snap["items"]
        ],
        "subtotal": snap["subtotal"],
        "delivery_fee": snap["delivery_fee"],
        "total": snap["total"],
        "delivery_address": delivery_address or "Default address",
        "placed_at": time.time(),
    }
    _orders[oid] = order
    _latest_order_id = oid
    status, eta = _derive_status(order["placed_at"])
    return {
        "order_id": oid,
        "restaurant": order["restaurant"],
        "items": order["items"],
        "subtotal": order["subtotal"],
        "delivery_fee": order["delivery_fee"],
        "total": order["total"],
        "delivery_address": order["delivery_address"],
        "status": status,
        "eta": eta,
    }


def get_order_status(order_id: str | None = None) -> dict[str, Any]:
    """Return current (time-derived) status of an order. Defaults to latest order."""
    oid = order_id or _latest_order_id
    if not oid or oid not in _orders:
        return {"error": "No order found. Place an order first."}
    order = _orders[oid]
    status, eta = _derive_status(order["placed_at"])
    return {
        "order_id": oid,
        "restaurant": order["restaurant"],
        "items": order["items"],
        "subtotal": order["subtotal"],
        "delivery_fee": order["delivery_fee"],
        "total": order["total"],
        "status": status,
        "eta": eta,
    }
