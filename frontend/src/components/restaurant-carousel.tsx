import { RestaurantCard, RestaurantCardProps } from "@/components/restaurant-card";
import { z } from "zod";

export const RestaurantCarouselProps = z.object({
  title: z.string().optional().describe("Optional heading above the carousel"),
  restaurants: z
    .array(RestaurantCardProps)
    .min(1)
    .describe("Restaurants to display as horizontally-scrolling cards"),
});

type RestaurantCarouselProps = z.infer<typeof RestaurantCarouselProps>;

export function RestaurantCarousel({
  title,
  restaurants,
}: Partial<RestaurantCarouselProps>) {
  const list = restaurants ?? [];
  if (list.length === 0) return null;

  return (
    <div className="max-w-full space-y-2">
      {title && (
        <div className="text-sm font-semibold text-gray-900">{title}</div>
      )}
      <div className="flex gap-3 overflow-x-auto pb-2 snap-x snap-mandatory">
        {list.map((r, i) => (
          <div key={i} className="shrink-0 w-72 snap-start">
            <RestaurantCard {...r} />
          </div>
        ))}
      </div>
    </div>
  );
}
