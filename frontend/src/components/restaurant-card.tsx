import { z } from "zod";

export const RestaurantCardProps = z.object({
  name: z.string().describe("Restaurant name"),
  cuisine: z.string().describe("Cuisine type, e.g. Lebanese, Italian, Burgers"),
  rating: z.number().min(0).max(5).describe("Average rating, 0–5"),
  delivery_time: z.string().describe("Estimated delivery time, e.g. '25–35 min'"),
  delivery_fee: z.string().describe("Delivery fee display, e.g. 'AED 5' or 'Free'"),
  tags: z
    .array(z.string())
    .optional()
    .describe("Short tags like 'Free delivery', 'Top eats'"),
});

type RestaurantCardProps = z.infer<typeof RestaurantCardProps>;

const BRAND = "#EB6030";

export function RestaurantCard({
  name,
  cuisine,
  rating,
  delivery_time,
  delivery_fee,
  tags,
}: Partial<RestaurantCardProps>) {
  const initial = (name ?? "").charAt(0).toUpperCase() || "?";
  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden max-w-sm">
      <div
        className="h-24 flex items-center justify-center text-white text-3xl font-bold tracking-wide"
        style={{ backgroundColor: BRAND }}
      >
        {initial}
      </div>
      <div className="p-4 space-y-2">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-base font-semibold text-gray-900">{name ?? "…"}</div>
            <div className="text-xs text-gray-500">{cuisine ?? ""}</div>
          </div>
          {typeof rating === "number" && (
            <div
              className="flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold text-white"
              style={{ backgroundColor: BRAND }}
            >
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.922-.755 1.688-1.54 1.118l-3.37-2.448a1 1 0 00-1.175 0l-3.37 2.448c-.784.57-1.838-.196-1.539-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.05 9.384c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69l1.286-3.957z" />
              </svg>
              {rating.toFixed(1)}
            </div>
          )}
        </div>
        <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 2m6-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {delivery_time ?? "—"}
          </div>
          <div className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 7h13l-1.5 9H4.5L3 7zm0 0L2 3H0m7 14a2 2 0 11-4 0 2 2 0 014 0zm10 0a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            {delivery_fee ?? "—"}
          </div>
        </div>
        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-2">
            {tags.map((t, i) => (
              <span
                key={i}
                className="text-[10px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 border border-orange-100"
              >
                {t}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
