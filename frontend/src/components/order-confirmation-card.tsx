import { z } from "zod";

export const OrderConfirmationCardProps = z.object({
  order_id: z.string().describe("Short order id, e.g. 'TLB-8821'"),
  restaurant: z.string().describe("Restaurant fulfilling the order"),
  items: z
    .array(
      z.object({
        name: z.string().describe("Item name"),
        quantity: z.number().int().min(1).describe("Quantity ordered"),
      }),
    )
    .min(1)
    .describe("Items in the order"),
  total: z.string().describe("Grand total, e.g. 'AED 150'"),
  eta: z.string().describe("Estimated time of arrival, e.g. '25 min'"),
  delivery_address: z.string().optional().describe("Delivery address"),
});

type OrderConfirmationCardProps = z.infer<typeof OrderConfirmationCardProps>;

const BRAND = "#EB6030";

export function OrderConfirmationCard({
  order_id,
  restaurant,
  items,
  total,
  eta,
  delivery_address,
}: Partial<OrderConfirmationCardProps>) {
  const list = items ?? [];
  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden max-w-sm">
      <div
        className="px-4 py-4 text-white flex items-center gap-3"
        style={{ backgroundColor: BRAND }}
      >
        <div
          className="w-9 h-9 rounded-full bg-white flex items-center justify-center shrink-0"
          style={{ color: BRAND }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div className="min-w-0">
          <div className="text-[11px] uppercase tracking-wider opacity-90">Order placed</div>
          <div className="text-sm font-semibold truncate">{order_id ?? "…"}</div>
        </div>
      </div>

      <div className="px-4 py-3 space-y-1">
        <div className="text-[11px] uppercase tracking-wider text-gray-500">Restaurant</div>
        <div className="text-sm font-semibold text-gray-900">{restaurant ?? "…"}</div>
      </div>

      <div className="px-4 py-3 border-t border-gray-100 space-y-1.5">
        {list.map((item, i) => (
          <div key={i} className="flex items-center justify-between text-xs text-gray-700">
            <span className="truncate">
              <span className="font-semibold mr-1">{item?.quantity ?? 1}×</span>
              {item?.name ?? ""}
            </span>
          </div>
        ))}
      </div>

      <div className="px-4 py-3 border-t border-gray-100 bg-gray-50 grid grid-cols-2 gap-3">
        <div>
          <div className="text-[10px] uppercase tracking-wider text-gray-500">ETA</div>
          <div className="text-sm font-semibold text-gray-900">{eta ?? "—"}</div>
        </div>
        <div className="text-right">
          <div className="text-[10px] uppercase tracking-wider text-gray-500">Total</div>
          <div className="text-sm font-bold" style={{ color: BRAND }}>{total ?? "—"}</div>
        </div>
        {delivery_address && (
          <div className="col-span-2 pt-2 border-t border-gray-200">
            <div className="text-[10px] uppercase tracking-wider text-gray-500">Delivering to</div>
            <div className="text-xs text-gray-700 truncate">{delivery_address}</div>
          </div>
        )}
      </div>
    </div>
  );
}
