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


# ── Cart state ────────────────────────────────────────────────────────────────

_PRICE_RE = re.compile(r"AED\s*(\d+(?:\.\d+)?)", re.IGNORECASE)


def _parse_price(s: str) -> float:
    if not s:
        return 0.0
    m = _PRICE_RE.search(s)
    return float(m.group(1)) if m else 0.0


# Demo-scoped singleton cart (one conversation = one cart).
_cart: dict[str, int] = {}
_cart_restaurant_id: str | None = None


def _cart_snapshot() -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    subtotal = 0.0
    for iid, qty in _cart.items():
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
    restaurant = (
        _RESTAURANT_INDEX.get(_cart_restaurant_id)
        if _cart_restaurant_id else None
    )
    delivery_fee_val = _parse_price(restaurant["delivery_fee"]) if restaurant else 0.0
    total = subtotal + delivery_fee_val
    return {
        "restaurant_id": _cart_restaurant_id,
        "restaurant": restaurant["name"] if restaurant else None,
        "items": items,
        "subtotal": f"AED {subtotal:.0f}",
        "delivery_fee": restaurant["delivery_fee"] if restaurant else "Free",
        "total": f"AED {total:.0f}",
        "item_count": sum(_cart.values()),
    }


def add_to_cart(item_id: str, quantity: int = 1) -> dict[str, Any]:
    """Add `quantity` of an item to the cart. Switching restaurants replaces the cart."""
    global _cart, _cart_restaurant_id
    item = _ITEM_INDEX.get(item_id)
    if not item:
        return {"error": f"Unknown item id: {item_id}", "cart": _cart_snapshot()}
    qty = max(1, int(quantity))
    if _cart_restaurant_id is None:
        _cart_restaurant_id = item["restaurant_id"]
    elif _cart_restaurant_id != item["restaurant_id"]:
        _cart = {}
        _cart_restaurant_id = item["restaurant_id"]
    _cart[item_id] = _cart.get(item_id, 0) + qty
    return _cart_snapshot()


def update_cart_item(item_id: str, quantity: int) -> dict[str, Any]:
    """Set the exact quantity for an item; quantity ≤ 0 removes it."""
    global _cart, _cart_restaurant_id
    if quantity <= 0:
        _cart.pop(item_id, None)
    else:
        item = _ITEM_INDEX.get(item_id)
        if not item:
            return {"error": f"Unknown item id: {item_id}", "cart": _cart_snapshot()}
        if _cart_restaurant_id is None:
            _cart_restaurant_id = item["restaurant_id"]
        elif _cart_restaurant_id != item["restaurant_id"]:
            _cart = {}
            _cart_restaurant_id = item["restaurant_id"]
        _cart[item_id] = int(quantity)
    if not _cart:
        _cart_restaurant_id = None
    return _cart_snapshot()


def remove_from_cart(item_id: str) -> dict[str, Any]:
    return update_cart_item(item_id, 0)


def clear_cart() -> dict[str, Any]:
    global _cart, _cart_restaurant_id
    _cart = {}
    _cart_restaurant_id = None
    return _cart_snapshot()


def view_cart() -> dict[str, Any]:
    return _cart_snapshot()


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


def place_order(delivery_address: str | None = None) -> dict[str, Any]:
    """Convert the current cart into an order and clear the cart."""
    global _cart, _cart_restaurant_id, _latest_order_id
    snap = _cart_snapshot()
    if not snap["items"]:
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
    _cart = {}
    _cart_restaurant_id = None
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
