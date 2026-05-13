import { MenuItemCard, MenuItemCardProps } from "@/components/menu-item-card";
import { z } from "zod";

export const MenuItemCarouselProps = z.object({
  title: z.string().optional().describe("Optional heading above the carousel"),
  items: z
    .array(MenuItemCardProps)
    .min(1)
    .describe("Menu items to display as horizontally-scrolling cards"),
});

type MenuItemCarouselProps = z.infer<typeof MenuItemCarouselProps>;

export function MenuItemCarousel({
  title,
  items,
}: Partial<MenuItemCarouselProps>) {
  const list = items ?? [];
  if (list.length === 0) return null;

  return (
    <div className="max-w-full space-y-2">
      {title && (
        <div className="text-sm font-semibold text-gray-900">{title}</div>
      )}
      <div className="flex gap-3 overflow-x-auto pb-2 snap-x snap-mandatory">
        {list.map((item, i) => (
          <div key={i} className="shrink-0 w-80 snap-start">
            <MenuItemCard {...item} />
          </div>
        ))}
      </div>
    </div>
  );
}
