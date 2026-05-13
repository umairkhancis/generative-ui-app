import { z } from "zod";

export const CartSummaryCardProps = z.object({
  restaurant: z.string().describe("Restaurant the cart is from"),
  items: z
    .array(
      z.object({
        name: z.string().describe("Item name"),
        quantity: z.number().int().min(1).describe("Quantity ordered"),
        price: z.string().describe("Unit price display, e.g. 'AED 32'"),
        line_total: z.string().optional().describe("Quantity × price, e.g. 'AED 96'"),
      }),
    )
    .min(1)
    .describe("Line items currently in the cart"),
  subtotal: z.string().describe("Cart subtotal, e.g. 'AED 145'"),
  delivery_fee: z.string().describe("Delivery fee display, e.g. 'AED 5' or 'Free'"),
  total: z.string().describe("Grand total, e.g. 'AED 150'"),
});

type CartSummaryCardProps = z.infer<typeof CartSummaryCardProps>;

const BRAND = "#EB6030";

export function CartSummaryCard({
  restaurant,
  items,
  subtotal,
  delivery_fee,
  total,
}: Partial<CartSummaryCardProps>) {
  const list = items ?? [];
  if (list.length === 0) return null;
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

      <div className="px-4 py-3 space-y-2 max-h-64 overflow-y-auto">
        {list.map((item, i) => (
          <div key={i} className="flex items-start justify-between gap-3 text-sm">
            <div className="min-w-0 flex items-baseline gap-2">
              <span
                className="text-[11px] font-bold rounded px-1.5 py-0.5 shrink-0"
                style={{ backgroundColor: "#FDEAE0", color: BRAND }}
              >
                {item?.quantity ?? 1}×
              </span>
              <span className="text-gray-900 truncate">{item?.name ?? "…"}</span>
            </div>
            <div className="text-right shrink-0">
              <div className="text-sm text-gray-900 whitespace-nowrap">
                {item?.line_total ?? item?.price ?? "—"}
              </div>
              {item?.line_total && item?.price && (
                <div className="text-[10px] text-gray-400 whitespace-nowrap">
                  {item.quantity ?? 1} × {item.price}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="px-4 py-3 border-t border-gray-100 bg-gray-50 space-y-1 text-sm">
        <div className="flex items-center justify-between text-gray-600">
          <span>Subtotal</span>
          <span>{subtotal ?? "—"}</span>
        </div>
        <div className="flex items-center justify-between text-gray-600">
          <span>Delivery</span>
          <span>{delivery_fee ?? "—"}</span>
        </div>
        <div className="flex items-center justify-between pt-1 border-t border-gray-200">
          <span className="font-semibold text-gray-900">Total</span>
          <span className="font-bold text-gray-900">{total ?? "—"}</span>
        </div>
      </div>
    </div>
  );
}
