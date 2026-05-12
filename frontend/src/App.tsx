import { CopilotChat } from "@copilotkit/react-core/v2";
import { TodoAppLayout } from "@/components/todo-app-layout";
import { TodoList } from "@/components/todo-list";
import { useExampleFixedSuggestions, useExampleSuggestions, useTodoSuggestions } from "@/hooks/use-example-suggestions";
import { useAgent, useFrontendTool } from "@copilotkit/react-core/v2";
import { useState } from "react";
import { z } from "zod";
import { useControlledComponents } from "./hooks/use-controlled-components";

const params = new URLSearchParams(typeof window !== "undefined" ? window.location.search : "");
const agentId = (params.get("agent") as string) || "default";

// Suggestions must be called inside the CopilotChat context, not outside it.
function ChatWithSuggestions() {
  useControlledComponents();
  useExampleSuggestions();
  useExampleFixedSuggestions();
  useTodoSuggestions();
  // useExampleDynamicSuggestions(); // Dynamic Schema: NOT WORKING
  return <CopilotChat agentId={agentId} />;
}

export default function App() {
  const [todosOpen, setTodosOpen] = useState(false);

  // 🪁 Register a frontend tool the agent can call to control the UI
  useFrontendTool({
    name: "openOrCloseTodos",
    description: "Open or close the todo panel.",
    parameters: z.object({ open: z.boolean() }),
    handler: async ({ open }) => {
      setTodosOpen(open);
      return `Todos are ${open ? 'open' : 'closed'}.`;
    },
  });

  // 🪁 Subscribe to shared agent state
  const { agent } = useAgent({ agentId: "default" });

  return (
    <TodoAppLayout
      chat={<ChatWithSuggestions />}
      open={todosOpen}
      onOpenChange={setTodosOpen}
      panel={(onClose) => (
        <TodoList
          // 🪁 Read shared state
          todos={agent.state.todos || []}

          // 🪁 Write shared state
          onUpdate={(updated) => agent.setState({ todos: updated })}

          isRunning={agent.isRunning}
          onClose={onClose}
        />
      )}
    />
  );
};
