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

export const useTodoSuggestions = () => {
  useConfigureSuggestions({
    suggestions: [
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
