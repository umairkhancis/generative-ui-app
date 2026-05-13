import { z } from "zod";

const STATUSES = ["confirming", "preparing", "delivering", "delivered"] as const;

export const OrderTrackingCardProps = z.object({
  order_id: z.string().describe("Short order id, e.g. 'TLB-8821'"),
  restaurant: z.string().describe("Restaurant fulfilling the order"),
  status: z
    .enum(STATUSES)
    .describe("Current order status in the progression"),
  eta: z.string().describe("Estimated time of arrival, e.g. '20 min'"),
  items: z
    .array(
      z.object({
        name: z.string().describe("Item name"),
        quantity: z.number().int().min(1).describe("Item quantity"),
      }),
    )
    .min(1)
    .describe("Items in the order"),
  total: z.string().describe("Order total display, e.g. 'AED 84'"),
});

type OrderTrackingCardProps = z.infer<typeof OrderTrackingCardProps>;

const BRAND = "#EB6030";

const STATUS_LABELS: Record<(typeof STATUSES)[number], string> = {
  confirming: "Confirming",
  preparing: "Preparing",
  delivering: "On the way",
  delivered: "Delivered",
};

export function OrderTrackingCard({
  order_id,
  restaurant,
  status,
  eta,
  items,
  total,
}: Partial<OrderTrackingCardProps>) {
  const currentIndex = status ? STATUSES.indexOf(status) : -1;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden max-w-sm">
      <div
        className="px-4 py-3 text-white flex items-center justify-between gap-4"
        style={{ backgroundColor: BRAND }}
      >
        <div className="min-w-0">
          <div className="text-[11px] uppercase tracking-wider opacity-80">Order {order_id ?? "…"}</div>
          <div className="text-sm font-semibold truncate">{restaurant ?? "…"}</div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-[11px] uppercase tracking-wider opacity-80">ETA</div>
          <div className="text-sm font-semibold whitespace-nowrap">{eta ?? "—"}</div>
        </div>
      </div>

      <div className="px-3 pt-4 pb-3">
        <div className="flex items-start">
          {STATUSES.map((s, i) => {
            const reached = i <= currentIndex;
            return (
              <div key={s} className="flex-1 flex flex-col items-center">
                <div className="w-full flex items-center">
                  <div
                    className="flex-1 h-0.5"
                    style={{
                      backgroundColor:
                        i === 0 ? "transparent" : i - 1 < currentIndex ? BRAND : "#e5e7eb",
                    }}
                  />
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 shrink-0"
                    style={{
                      backgroundColor: reached ? BRAND : "#fff",
                      borderColor: reached ? BRAND : "#e5e7eb",
                      color: reached ? "#fff" : "#9ca3af",
                    }}
                  >
                    {i + 1}
                  </div>
                  <div
                    className="flex-1 h-0.5"
                    style={{
                      backgroundColor:
                        i === STATUSES.length - 1 ? "transparent" : i < currentIndex ? BRAND : "#e5e7eb",
                    }}
                  />
                </div>
                <div
                  className="text-[10px] mt-1.5 leading-tight text-center px-0.5 whitespace-nowrap"
                  style={{
                    color: i <= currentIndex ? BRAND : "#6b7280",
                    fontWeight: i === currentIndex ? 600 : 400,
                  }}
                >
                  {STATUS_LABELS[s]}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="px-4 py-3 border-t border-gray-100 space-y-1.5">
        {(items ?? []).map((item, i) => (
          <div key={i} className="flex items-center justify-between text-xs text-gray-700">
            <span className="truncate">
              <span className="font-semibold mr-1">{item?.quantity ?? 1}×</span>
              {item?.name ?? ""}
            </span>
          </div>
        ))}
      </div>

      <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between bg-gray-50">
        <span className="text-xs text-gray-500">Total</span>
        <span className="text-base font-bold text-gray-900">{total ?? "—"}</span>
      </div>
    </div>
  );
}
