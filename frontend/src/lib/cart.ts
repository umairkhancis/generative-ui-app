// Shared cart math. Mirrors the backend snapshot shape from `food/cart.py`
// so the UI can mutate the cart client-side (CartPanel +/-, Clear) without
// a round-trip, and the agent reads the same shape on the next turn via
// shared state.

export type CartItem = {
  id: string;
  name: string;
  restaurant?: string;
  price: string;
  quantity: number;
  line_total?: string;
};

export type Cart = {
  restaurant_id: string | null;
  restaurant: string | null;
  items: CartItem[];
  subtotal: string;
  delivery_fee: string;
  total: string;
  item_count: number;
};

export function parsePrice(s: string | undefined | null): number {
  if (!s) return 0;
  const m = String(s).match(/AED\s*(\d+(?:\.\d+)?)/i);
  return m ? parseFloat(m[1]) : 0;
}

export function emptyCart(): Cart {
  return {
    restaurant_id: null,
    restaurant: null,
    items: [],
    subtotal: "AED 0",
    delivery_fee: "Free",
    total: "AED 0",
    item_count: 0,
  };
}

// Recompute line totals + summary from a (possibly mutated) items list.
export function recompute(
  items: CartItem[],
  deliveryFee: string | undefined | null,
  restaurantId: string | null,
  restaurant: string | null,
): Cart {
  let subtotal = 0;
  const updated = items
    .filter((i) => (i.quantity ?? 0) > 0)
    .map((i) => {
      const unit = parsePrice(i.price);
      const line = unit * (i.quantity ?? 0);
      subtotal += line;
      return { ...i, line_total: `AED ${Math.round(line)}` };
    });
  const feeVal = parsePrice(deliveryFee);
  const total = subtotal + feeVal;
  const hasItems = updated.length > 0;
  return {
    restaurant_id: hasItems ? restaurantId : null,
    restaurant: hasItems ? restaurant : null,
    items: updated,
    subtotal: `AED ${Math.round(subtotal)}`,
    delivery_fee: hasItems ? (deliveryFee || "Free") : "Free",
    total: `AED ${Math.round(total)}`,
    item_count: updated.reduce((s, i) => s + (i.quantity ?? 0), 0),
  };
}

export function setQuantity(
  cart: Cart | undefined | null,
  itemId: string,
  quantity: number,
): Cart {
  const current = cart ?? emptyCart();
  const next = current.items.map((i) =>
    i.id === itemId ? { ...i, quantity: Math.max(0, quantity) } : i,
  );
  return recompute(next, current.delivery_fee, current.restaurant_id, current.restaurant);
}
