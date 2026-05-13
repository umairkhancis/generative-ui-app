import { useAgent } from "@copilotkit/react-core/v2";
import { z } from "zod";

const CartItemSchema = z.object({
  id: z.string().describe("Item id, e.g. 'r-001-i-007' — required for +/- to work"),
  name: z.string().describe("Item name"),
  quantity: z.number().int().min(0).describe("Current quantity"),
  price: z.string().describe("Unit price display, e.g. 'AED 32'"),
  line_total: z.string().optional().describe("Quantity × price, e.g. 'AED 96'"),
  restaurant: z.string().optional(),
});

export const CartSummaryCardProps = z.object({
  restaurant: z.string().optional().describe("Restaurant the cart is from"),
  restaurant_id: z.string().optional().describe("Restaurant id"),
  items: z.array(CartItemSchema).optional().describe("Line items in the cart"),
  subtotal: z.string().optional().describe("Cart subtotal"),
  delivery_fee: z.string().optional().describe("Delivery fee display"),
  total: z.string().optional().describe("Grand total"),
});

type CartItem = z.infer<typeof CartItemSchema>;
type CartSummaryCardProps = z.infer<typeof CartSummaryCardProps>;

const BRAND = "#EB6030";

function parsePrice(s: string | undefined | null): number {
  if (!s) return 0;
  const m = String(s).match(/AED\s*(\d+(?:\.\d+)?)/i);
  return m ? parseFloat(m[1]) : 0;
}

function recompute(items: CartItem[], deliveryFee: string | undefined | null) {
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
  return {
    items: updated,
    subtotal: `AED ${Math.round(subtotal)}`,
    delivery_fee: deliveryFee || "Free",
    total: `AED ${Math.round(total)}`,
    item_count: updated.reduce((s, i) => s + (i.quantity ?? 0), 0),
  };
}

export function CartSummaryCard(props: Partial<CartSummaryCardProps>) {
  const { agent } = useAgent({ agentId: "default" });
  const stateCart = (agent.state as { cart?: Partial<CartSummaryCardProps> } | undefined)?.cart;

  // Prefer shared state — it's the source of truth once mutated by either side.
  const source: Partial<CartSummaryCardProps> = stateCart ?? props ?? {};
  const items: CartItem[] = (source.items as CartItem[] | undefined) ?? [];
  const restaurant = source.restaurant ?? null;
  const restaurantId = (source as { restaurant_id?: string }).restaurant_id ?? null;
  const deliveryFee = source.delivery_fee;
  const subtotal = source.subtotal;
  const total = source.total;

  const writeBack = (nextItems: CartItem[]) => {
    const rc = recompute(nextItems, deliveryFee);
    agent.setState({
      cart: {
        restaurant_id: rc.items.length ? restaurantId : null,
        restaurant: rc.items.length ? restaurant : null,
        ...rc,
      },
    });
  };

  const setQuantity = (itemId: string, newQty: number) => {
    if (agent.isRunning) return;
    const next = items.map((i) =>
      i.id === itemId ? { ...i, quantity: Math.max(0, newQty) } : i,
    );
    writeBack(next);
  };

  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden max-w-sm">
        <div
          className="px-4 py-3 text-white"
          style={{ backgroundColor: BRAND }}
        >
          <div className="text-[11px] uppercase tracking-wider opacity-80">Your cart</div>
          <div className="text-sm font-semibold">Empty</div>
        </div>
        <div className="px-4 py-6 text-center text-sm text-gray-500">
          Add items from a restaurant to get started.
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden max-w-sm">
      <div
        className="px-4 py-3 text-white flex items-center justify-between"
        style={{ backgroundColor: BRAND }}
      >
        <div>
          <div className="text-[11px] uppercase tracking-wider opacity-80">Your cart</div>
          <div className="text-sm font-semibold truncate">{restaurant ?? "…"}</div>
        </div>
        <svg className="w-5 h-5 opacity-90" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>

      <div className="px-4 py-3 space-y-2 max-h-72 overflow-y-auto">
        {items.map((item) => {
          const qty = item.quantity ?? 0;
          const disabled = agent.isRunning;
          return (
            <div key={item.id} className="flex items-center justify-between gap-3 text-sm">
              <div className="min-w-0 flex items-center gap-2">
                <div
                  className="flex items-center gap-1 shrink-0"
                  style={{ opacity: disabled ? 0.5 : 1 }}
                >
                  <button
                    type="button"
                    onClick={() => setQuantity(item.id, qty - 1)}
                    disabled={disabled}
                    aria-label={`Decrease ${item.name}`}
                    className="w-6 h-6 rounded-full border border-gray-300 text-gray-700 flex items-center justify-center hover:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M20 12H4" />
                    </svg>
                  </button>
                  <span
                    className="text-[12px] font-bold w-6 text-center"
                    style={{ color: BRAND }}
                  >
                    {qty}
                  </span>
                  <button
                    type="button"
                    onClick={() => setQuantity(item.id, qty + 1)}
                    disabled={disabled}
                    aria-label={`Increase ${item.name}`}
                    className="w-6 h-6 rounded-full text-white flex items-center justify-center disabled:cursor-not-allowed"
                    style={{ backgroundColor: BRAND }}
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>
                <span className="text-gray-900 truncate">{item.name}</span>
              </div>
              <div className="text-right shrink-0">
                <div className="text-sm text-gray-900 whitespace-nowrap">
                  {item.line_total ?? `AED ${Math.round(parsePrice(item.price) * qty)}`}
                </div>
                <div className="text-[10px] text-gray-400 whitespace-nowrap">
                  {qty} × {item.price}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="px-4 py-3 border-t border-gray-100 bg-gray-50 space-y-1 text-sm">
        <div className="flex items-center justify-between text-gray-600">
          <span>Subtotal</span>
          <span>{subtotal ?? "—"}</span>
        </div>
        <div className="flex items-center justify-between text-gray-600">
          <span>Delivery</span>
          <span>{deliveryFee ?? "—"}</span>
        </div>
        <div className="flex items-center justify-between pt-1 border-t border-gray-200">
          <span className="font-semibold text-gray-900">Total</span>
          <span className="font-bold text-gray-900">{total ?? "—"}</span>
        </div>
      </div>
    </div>
  );
}
