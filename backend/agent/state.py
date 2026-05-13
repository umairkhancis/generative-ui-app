"""Shared agent state — auto-synced with the React frontend.

Anything added to `AgentState` here is auto-synced with the frontend.
The React side reads via `useAgent({agentId: "default"}).state.<field>`
and writes via `.setState({<field>: ...})`. Tool-side writes come from
`Command(update={<field>: ...})` (see `tools.py`).
"""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain.agents import AgentState as BaseAgentState


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


def last_write_wins(_old: Any, new: Any) -> Any:
    """Reducer for state channels that may receive >1 write per step.

    Both the frontend (`agent.setState({cart})`) and tool-side `Command`
    updates can land in the same LangGraph tick — without a reducer, that
    raises `InvalidUpdateError`. For a cart, "the latest snapshot wins" is
    correct: every snapshot is self-contained, so we don't need to merge.
    """
    return new


class AgentState(BaseAgentState):
    cart: Annotated[Cart, last_write_wins]
