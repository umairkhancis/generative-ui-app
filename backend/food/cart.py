"""Pure cart operations.

The cart "lives" in LangGraph AgentState (shared with the frontend canvas
card). These functions are pure: given a current cart snapshot they
return a new snapshot. They never mutate global state.

Cart snapshot shape:
    {
      restaurant_id: str | None,
      restaurant:    str | None,
      items:         [{id, name, restaurant, price, quantity, line_total}, ...],
      subtotal:      "AED N",
      delivery_fee:  "AED N" | "Free",
      total:         "AED N",
      item_count:    int,
    }
"""

from __future__ import annotations

import re
from typing import Any

from food.catalog import ITEM_INDEX, RESTAURANT_INDEX

_PRICE_RE = re.compile(r"AED\s*(\d+(?:\.\d+)?)", re.IGNORECASE)


def _parse_price(s: str) -> float:
    if not s:
        return 0.0
    m = _PRICE_RE.search(s)
    return float(m.group(1)) if m else 0.0


def _compute_snapshot(
    quantities: dict[str, int], restaurant_id: str | None
) -> dict[str, Any]:
    """Build a complete cart snapshot from {item_id: quantity} + restaurant id."""
    items: list[dict[str, Any]] = []
    subtotal = 0.0
    for iid, qty in quantities.items():
        if qty <= 0:
            continue
        item = ITEM_INDEX.get(iid)
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
    restaurant = RESTAURANT_INDEX.get(restaurant_id) if restaurant_id else None
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
    quantities = {
        i["id"]: int(i.get("quantity") or 0)
        for i in cart.get("items", []) or []
    }
    return quantities, cart.get("restaurant_id")


def empty_cart() -> dict[str, Any]:
    """The canonical empty-cart snapshot."""
    return _compute_snapshot({}, None)


def cart_add(
    cart: dict[str, Any] | None, item_id: str, quantity: int = 1
) -> dict[str, Any]:
    """Add `quantity` of an item. Switching restaurants resets the cart."""
    item = ITEM_INDEX.get(item_id)
    if not item:
        return cart or empty_cart()
    qty = max(1, int(quantity))
    quantities, rid = _quantities_from_cart(cart)
    if rid is None:
        rid = item["restaurant_id"]
    elif rid != item["restaurant_id"]:
        quantities = {}
        rid = item["restaurant_id"]
    quantities[item_id] = quantities.get(item_id, 0) + qty
    return _compute_snapshot(quantities, rid)


def cart_update(
    cart: dict[str, Any] | None, item_id: str, quantity: int
) -> dict[str, Any]:
    """Set the exact quantity. quantity <= 0 removes the item."""
    quantities, rid = _quantities_from_cart(cart)
    if quantity <= 0:
        quantities.pop(item_id, None)
    else:
        item = ITEM_INDEX.get(item_id)
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
