// CONTROLLED GENERATIVE UI — registration site.
//
// `useComponent` (from @copilotkit/react-core/v2) tells the CopilotKit runtime
// that a named React component is callable by the agent as if it were a tool.
// When the agent calls e.g. `restaurantCarousel({ restaurants: [...] })`,
// the runtime invokes `render(args)` here and inserts the rendered React
// element inline in the chat transcript. The `parameters` Zod schema is
// surfaced to the LLM so it knows the expected shape.
//
// Every component listed below is a "controlled" GenUI component: developer
// has defined the visual + the schema, the agent decides when to render it
// and supplies the data.
import { CartSummaryCard, CartSummaryCardProps } from "@/components/cart-summary-card";
import { MenuItemCard, MenuItemCardProps } from "@/components/menu-item-card";
import { MenuItemCarousel, MenuItemCarouselProps } from "@/components/menu-item-carousel";
import { OrderConfirmationCard, OrderConfirmationCardProps } from "@/components/order-confirmation-card";
import { OrderTrackingCard, OrderTrackingCardProps } from "@/components/order-tracking-card";
import { RestaurantCard, RestaurantCardProps } from "@/components/restaurant-card";
import { RestaurantCarousel, RestaurantCarouselProps } from "@/components/restaurant-carousel";
import { useComponent } from "@copilotkit/react-core/v2";

export const useControlledComponents = () => {
  // Single-restaurant card.
  useComponent({
    name: "restaurantCard",
    description:
      "Controlled Generative UI that displays a single restaurant card with cuisine, rating, delivery time and fee.",
    parameters: RestaurantCardProps,
    render: RestaurantCard,
  });

  // Single-menu-item card.
  useComponent({
    name: "menuItemCard",
    description:
      "Controlled Generative UI that displays a single menu item with name, description, price and dietary tags.",
    parameters: MenuItemCardProps,
    render: MenuItemCard,
  });

  // Horizontal carousel of restaurant cards — preferred over multiple
  // single-card calls when showing several restaurants together.
  useComponent({
    name: "restaurantCarousel",
    description:
      "Controlled Generative UI that displays a horizontal carousel of restaurant cards. Prefer this over multiple `restaurantCard` calls whenever showing more than one restaurant (e.g. discovery / browse results).",
    parameters: RestaurantCarouselProps,
    render: RestaurantCarousel,
  });

  // Horizontal carousel of menu items.
  useComponent({
    name: "menuItemCarousel",
    description:
      "Controlled Generative UI that displays a horizontal carousel of menu items. Prefer this over multiple `menuItemCard` calls whenever showing more than one item (e.g. a restaurant's menu or recommended dishes).",
    parameters: MenuItemCarouselProps,
    render: MenuItemCarousel,
  });

  // Live cart card — also a SHARED-STATE canvas. The component subscribes
  // to `agent.state.cart` via `useAgent` and writes back with `setState`.
  // Tool-side updates flow in through `Command(update={cart: ...})` from the
  // backend, so both directions converge on a single source of truth.
  useComponent({
    name: "cartSummaryCard",
    description:
      "Controlled Generative UI that displays the current cart for review before checkout: restaurant, line items with quantities and prices, subtotal, delivery fee and total. Use this whenever showing or updating the cart.",
    parameters: CartSummaryCardProps,
    render: CartSummaryCard,
  });

  // After place_order succeeds — confirmation view.
  useComponent({
    name: "orderConfirmationCard",
    description:
      "Controlled Generative UI that confirms an order was placed: order id, restaurant, items, total, ETA and delivery address. Use immediately after place_order succeeds.",
    parameters: OrderConfirmationCardProps,
    render: OrderConfirmationCard,
  });

  // Live order tracking — status progresses with time on the backend.
  useComponent({
    name: "orderTrackingCard",
    description:
      "Controlled Generative UI that shows order tracking progression (confirming → preparing → delivering → delivered) with ETA and items.",
    parameters: OrderTrackingCardProps,
    render: OrderTrackingCard,
  });
};
