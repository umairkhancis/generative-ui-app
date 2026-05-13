"""Order placement and time-progressed status tracking.

`place_order` turns a cart snapshot into an order and stashes it in an
in-memory registry. `get_order_status` derives the current status (and
ETA) from elapsed wall-clock time since `placed_at`.

Compressed for demo — full lifecycle is ~3 minutes:
    0  – 30s : confirming
    30 – 90s : preparing
    90 – 180s: delivering
    180s+    : delivered
"""

from __future__ import annotations

import time
import uuid
from typing import Any

_orders: dict[str, dict[str, Any]] = {}
_latest_order_id: str | None = None

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
    """Turn a cart snapshot into an order. Caller is responsible for clearing the cart."""
    global _latest_order_id
    snap = cart or {}
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
    """Current (time-derived) status of an order. Defaults to the latest one."""
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
