import { CopilotChat } from "@copilotkit/react-core/v2";


import { useExampleDynamicSuggestions, useExampleFixedSuggestions, useExampleSuggestions } from "@/hooks/use-example-suggestions";
import { useControlledComponents } from "./hooks/use-controlled-components";

const params = new URLSearchParams(typeof window !== "undefined" ? window.location.search : "");
const agentId = (params.get("agent") as string) || "default";

export default function App() {

  useControlledComponents();
  
  useExampleSuggestions();
  useExampleDynamicSuggestions();
  useExampleFixedSuggestions();

  return <CopilotChat agentId={agentId} />;
};
