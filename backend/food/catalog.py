"""Restaurant + menu catalogue, backed by CSV files in `food/db/`.

Read-only. Loaded once at import time. The CSV files are seeded by
`backend/food/_seed.py`.

Each restaurant: id, name, cuisine, rating, delivery_time, delivery_fee, tags.
Each menu item:  id, restaurant_id, restaurant, name, description, price,
                 spicy, vegetarian, popular.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

_DB_DIR = Path(__file__).resolve().parent / "db"
_RESTAURANTS_CSV = _DB_DIR / "restaurants.csv"
_MENU_ITEMS_CSV = _DB_DIR / "menu_items.csv"


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


RESTAURANTS: list[dict[str, Any]] = _load_restaurants()
MENU_ITEMS: list[dict[str, Any]] = _load_menu_items()
RESTAURANT_INDEX: dict[str, dict[str, Any]] = {r["id"]: r for r in RESTAURANTS}
ITEM_INDEX: dict[str, dict[str, Any]] = {i["id"]: i for i in MENU_ITEMS}

_MENU_BY_RESTAURANT: dict[str, list[dict[str, Any]]] = {}
for _it in MENU_ITEMS:
    _MENU_BY_RESTAURANT.setdefault(_it["restaurant_id"], []).append(_it)


# ── Restaurant queries ────────────────────────────────────────────────────────

def list_restaurants(cuisine: str | None = None, limit: int = 12) -> list[dict[str, Any]]:
    """Discovery: return curated restaurants, top-rated first.

    Optional cuisine filter (case-insensitive exact match on the cuisine column).
    """
    pool = RESTAURANTS
    if cuisine:
        needle = cuisine.strip().lower()
        pool = [r for r in pool if r["cuisine"].lower() == needle]
    pool = sorted(pool, key=lambda r: -r["rating"])
    return pool[: max(0, limit)]


def search_restaurants(query: str, limit: int = 6) -> list[dict[str, Any]]:
    """Keyword search on restaurant name, cuisine and tags. Scored by relevance."""
    needle = (query or "").strip().lower()
    if not needle:
        return []
    scored: list[tuple[int, dict[str, Any]]] = []
    for r in RESTAURANTS:
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
    """Distinct cuisine names, alphabetised — useful for system-prompt hints."""
    return sorted({r["cuisine"] for r in RESTAURANTS})


# ── Menu queries ──────────────────────────────────────────────────────────────

def list_menu_items(restaurant_id: str, limit: int = 12) -> list[dict[str, Any]]:
    """Discovery: menu for one restaurant, popular items first then alphabetical."""
    pool = _MENU_BY_RESTAURANT.get(restaurant_id, [])
    pool = sorted(pool, key=lambda i: (not i["popular"], i["name"]))
    return pool[: max(0, limit)]


def search_menu_items(
    query: str,
    restaurant_id: str | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Keyword search on item name/description; optionally scoped to one restaurant."""
    needle = (query or "").strip().lower()
    if not needle:
        return []
    pool = (
        _MENU_BY_RESTAURANT.get(restaurant_id, [])
        if restaurant_id else MENU_ITEMS
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
