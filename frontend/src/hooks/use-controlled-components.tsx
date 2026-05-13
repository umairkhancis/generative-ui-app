import { CartSummaryCard, CartSummaryCardProps } from "@/components/cart-summary-card";
import { FlightCard, FlightCardProps } from "@/components/flight-card";
import { MenuItemCard, MenuItemCardProps } from "@/components/menu-item-card";
import { MenuItemCarousel, MenuItemCarouselProps } from "@/components/menu-item-carousel";
import { OrderConfirmationCard, OrderConfirmationCardProps } from "@/components/order-confirmation-card";
import { OrderTrackingCard, OrderTrackingCardProps } from "@/components/order-tracking-card";
import { PieChart, PieChartProps } from "@/components/pie-chart";
import { RestaurantCard, RestaurantCardProps } from "@/components/restaurant-card";
import { RestaurantCarousel, RestaurantCarouselProps } from "@/components/restaurant-carousel";
import { useComponent } from "@copilotkit/react-core/v2";
import { z } from "zod";

export const useControlledComponents = () => {
  // 🪁 Register a component that shows the name of the user
  useComponent({
    name: "showMyName",
    description: "Show the user's name in a card",
    parameters: z.object({ name: z.string() }),
    render: ({ name }) => <div className="bg-blue-500 p-4">Hi, {name}!</div>,
  });

  // 🪁 Resgister a pieChart component to show structured data
  useComponent({
    name: "pieChart",
    description: "Controlled Generative UI that displays data as a pie chart.",
    parameters: PieChartProps,
    render: PieChart,
  });

  // 🪁 Resgister a flightCard component to show flight data
  useComponent({
    name: "flightCard",
    description: "Controlled Generative UI that displays a single flight summary card.",
    parameters: FlightCardProps,
    render: FlightCard,
  });

  // 🪁 Register a restaurantCard component for food-delivery discovery
  useComponent({
    name: "restaurantCard",
    description:
      "Controlled Generative UI that displays a single restaurant card with cuisine, rating, delivery time and fee.",
    parameters: RestaurantCardProps,
    render: RestaurantCard,
  });

  // 🪁 Register a menuItemCard component for food-delivery menu browsing
  useComponent({
    name: "menuItemCard",
    description:
      "Controlled Generative UI that displays a single menu item with name, description, price and dietary tags.",
    parameters: MenuItemCardProps,
    render: MenuItemCard,
  });

  // 🪁 Register a restaurantCarousel for showing multiple restaurants together
  useComponent({
    name: "restaurantCarousel",
    description:
      "Controlled Generative UI that displays a horizontal carousel of restaurant cards. Prefer this over multiple `restaurantCard` calls whenever showing more than one restaurant (e.g. discovery / browse results).",
    parameters: RestaurantCarouselProps,
    render: RestaurantCarousel,
  });

  // 🪁 Register a menuItemCarousel for showing multiple menu items together
  useComponent({
    name: "menuItemCarousel",
    description:
      "Controlled Generative UI that displays a horizontal carousel of menu items. Prefer this over multiple `menuItemCard` calls whenever showing more than one item (e.g. a restaurant's menu or recommended dishes).",
    parameters: MenuItemCarouselProps,
    render: MenuItemCarousel,
  });

  // 🪁 Register an orderTrackingCard component for post-checkout tracking
  useComponent({
    name: "orderTrackingCard",
    description:
      "Controlled Generative UI that shows order tracking progression (confirming → preparing → delivering → delivered) with ETA and items.",
    parameters: OrderTrackingCardProps,
    render: OrderTrackingCard,
  });

  // 🪁 Register a cartSummaryCard for cart review during the ordering journey
  useComponent({
    name: "cartSummaryCard",
    description:
      "Controlled Generative UI that displays the current cart for review before checkout: restaurant, line items with quantities and prices, subtotal, delivery fee and total. Use this whenever showing or updating the cart.",
    parameters: CartSummaryCardProps,
    render: CartSummaryCard,
  });

  // 🪁 Register an orderConfirmationCard shown right after place_order
  useComponent({
    name: "orderConfirmationCard",
    description:
      "Controlled Generative UI that confirms an order was placed: order id, restaurant, items, total, ETA and delivery address. Use immediately after place_order succeeds.",
    parameters: OrderConfirmationCardProps,
    render: OrderConfirmationCard,
  });
};
