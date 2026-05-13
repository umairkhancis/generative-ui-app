import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

export const useExampleSuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
      {
        title: "Show my name",
        message:
          "Please show my name in the chat.",
      },
      {
        title: "Pie chart",
        message:
          "Please show me the distribution of our revenue by category in a pie chart.",
      },
      {
        title: "Flight card",
        message:
          "Show a flight card for Pacific Air from SFO to JFK departing at 08:30 for $249.",
      },
    ],
    available: "always",
  });
};

export const useExampleDynamicSuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
      {
        title: "Sales Dashboard",
        message:
          "Show me a sales dashboard with total revenue, new customers, and conversion rate metrics. Include a pie chart of revenue by category and a bar chart of monthly sales.",
      },
    ],
    available: "always",
  });
};

export const useExampleFixedSuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
      {
        title: "Search flights",
        message:
          "Find flights from San Francisco (SFO) to New York (JFK) for next Friday. Show me options from different airlines.",
      },
    ],
    available: "always",
  });
};

export const useFoodDeliverySuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
      {
        title: "Browse restaurants",
        message:
          "Show me top-rated restaurants nearby for delivery.",
      },
      {
        title: "Find a place",
        message:
          "Search for a falafel place.",
      },
      {
        title: "See the menu",
        message:
          "Show me the menu from Operation Falafel.",
      },
      {
        title: "Find a dish",
        message:
          "Find biryani options across restaurants.",
      },
      {
        title: "Add to cart",
        message:
          "Add 2 shawarma wraps and 1 hummus from Operation Falafel to my cart, then show me the cart.",
      },
      {
        title: "View cart",
        message:
          "Show me my cart.",
      },
      {
        title: "Place order",
        message:
          "Place my order. Deliver to 12 Sheikh Zayed Road.",
      },
      {
        title: "Track my order",
        message:
          "Where is my food? Show me the order tracking.",
      },
    ],
    available: "always",
  });
};

export const useTodoSuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
      {
        title: "Open todos",
        message: "Open the todos panel.",
      },
      {
        title: "Close todos",
        message: "Close the todos panel.",
      },
      {
        title: "Add todos",
        message: "Add three todos about learning CopilotKit",
      },
      {
        title: "Check my list",
        message: "What's on my todo list right now?",
      },
      {
        title: "Wrap up",
        message: "Mark all todos as completed and summarize what we did.",
      },
    ],
    available: "always",
  });
};
