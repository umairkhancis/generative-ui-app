import { AppLayout } from "@/components/app-layout";
import { CartPanel } from "@/components/cart-panel";
import { CopilotChat, useAgent, useFrontendTool } from "@copilotkit/react-core/v2";
import { useFoodDeliverySuggestions } from "@/hooks/use-example-suggestions";
import { type Cart } from "@/lib/cart";
import { useState } from "react";
import { z } from "zod";
import { useControlledComponents } from "./hooks/use-controlled-components";

const AGENT_ID = "default";

// Local view on agent.state — CopilotKit's `state` is untyped at the React
// boundary; declare what we expect so the rest of the file stays clean.
type SharedState = { cart?: Cart };

// Suggestions and controlled-component registrations must run inside the
// CopilotChat context, not outside it — that's the only place CopilotKit's
// React context is available.
function ChatWithSuggestions() {
  useControlledComponents();
  useFoodDeliverySuggestions();
  return <CopilotChat agentId={AGENT_ID} />;
}

export default function App() {
  const [cartOpen, setCartOpen] = useState(false);

  // 🪁 Frontend tool — lets the agent open/close the cart panel from chat.
  useFrontendTool({
    name: "openOrCloseCart",
    description: "Open or close the cart side panel.",
    parameters: z.object({ open: z.boolean() }),
    handler: async ({ open }) => {
      setCartOpen(open);
      return `Cart panel is ${open ? "open" : "closed"}.`;
    },
  });

  // 🪁 Subscribe to shared agent state. The panel reads `state.cart` and
  // writes back via `setState` — same state the cartSummaryCard (controlled
  // GenUI) and the backend `Command(update={cart: ...})` use.
  const { agent } = useAgent({ agentId: AGENT_ID });
  const cart = (agent.state as SharedState | undefined)?.cart;

  const requestCheckout = async () => {
    if (agent.isRunning) return;
    agent.addMessage({
      id: crypto.randomUUID(),
      role: "user",
      content: "Place my order. Deliver to 12 Sheikh Zayed Road.",
    });
    await agent.runAgent();
  };

  return (
    <AppLayout
      chat={<ChatWithSuggestions />}
      open={cartOpen}
      onOpenChange={setCartOpen}
      panelTitle="Cart"
      panel={(onClose) => (
        <CartPanel
          cart={cart}
          onUpdate={(updated) => agent.setState({ cart: updated })}
          onCheckout={requestCheckout}
          isRunning={agent.isRunning}
          onClose={onClose}
        />
      )}
    />
  );
}
