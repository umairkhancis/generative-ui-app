// Suggestion chips — pre-canned prompts shown above the chat input.
// `useConfigureSuggestions` is a thin registration; the `message` of each
// chip is sent verbatim when the user clicks it.
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

// Kept for reference — the todos panel is hidden from view but its code path
// is preserved. Re-enable in App.tsx + invoke this hook to bring it back.
export const useTodoSuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
      { title: "Open todos", message: "Open the todos panel." },
      { title: "Close todos", message: "Close the todos panel." },
      { title: "Add todos", message: "Add three todos about learning CopilotKit" },
      { title: "Check my list", message: "What's on my todo list right now?" },
      { title: "Wrap up", message: "Mark all todos as completed and summarize what we did." },
    ],
    available: "always",
  });
};
