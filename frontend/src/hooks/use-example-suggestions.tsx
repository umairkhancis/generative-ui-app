// Suggestion chips — pre-canned prompts shown above the chat input.
// `useConfigureSuggestions` is a thin registration; the `message` of each
// chip is sent verbatim when the user clicks it.
//
// The chips are deliberately ordered to trace the ordering journey
// (discovery → search → menu → cart → checkout → tracking) — so reading
// them left-to-right surfaces "what could you do next?" without any
// state-gating.
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

export const useFoodDeliverySuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
      {
        title: "Browse restaurants",
        message: "Show me top-rated restaurants nearby for delivery.",
      },
      {
        title: "Find a place",
        message: "Search for a falafel place.",
      },
      {
        title: "See the menu",
        message: "Show me the menu from Operation Falafel.",
      },
      {
        title: "Find a dish",
        message: "Find biryani options across restaurants.",
      },
      {
        title: "Add to cart",
        message:
          "Add 2 shawarma wraps and 1 hummus from Operation Falafel to my cart, then show me the cart.",
      },
      {
        title: "View cart",
        message: "Show me my cart.",
      },
      {
        title: "Place order",
        message: "Place my order. Deliver to 12 Sheikh Zayed Road.",
      },
      {
        title: "Track my order",
        message: "Where is my food? Show me the order tracking.",
      },
    ],
    available: "always",
  });
};
