import { z } from "zod";

export const MenuItemCardProps = z.object({
  name: z.string().describe("Menu item name"),
  description: z.string().describe("Short item description"),
  price: z.string().describe("Price display, e.g. 'AED 32'"),
  restaurant: z.string().optional().describe("Restaurant the item is from"),
  spicy: z.boolean().optional().describe("Whether the dish is spicy"),
  vegetarian: z.boolean().optional().describe("Whether the dish is vegetarian"),
  popular: z.boolean().optional().describe("Whether the dish is a popular pick"),
});

type MenuItemCardProps = z.infer<typeof MenuItemCardProps>;

const BRAND = "#EB6030";

export function MenuItemCard({
  name,
  description,
  price,
  restaurant,
  spicy,
  vegetarian,
  popular,
}: Partial<MenuItemCardProps>) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden max-w-sm flex">
      <div
        className="w-24 shrink-0 flex items-center justify-center text-white"
        style={{ backgroundColor: BRAND }}
      >
        <svg className="w-10 h-10" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 11h18M5 11V8a4 4 0 014-4h6a4 4 0 014 4v3M5 11v6a4 4 0 004 4h6a4 4 0 004-4v-6" />
        </svg>
      </div>
      <div className="p-3 flex-1 min-w-0 space-y-1.5">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="text-sm font-semibold text-gray-900 truncate">{name ?? "…"}</div>
            {restaurant && (
              <div className="text-[11px] text-gray-500 truncate">{restaurant}</div>
            )}
          </div>
          {price && (
            <div className="text-sm font-bold" style={{ color: BRAND }}>
              {price}
            </div>
          )}
        </div>
        <p className="text-xs text-gray-600 line-clamp-2">{description ?? ""}</p>
        <div className="flex flex-wrap gap-1 pt-1">
          {popular && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 border border-orange-100">
              Popular
            </span>
          )}
          {vegetarian && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-50 text-green-700 border border-green-100">
              Vegetarian
            </span>
          )}
          {spicy && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-100">
              Spicy
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
