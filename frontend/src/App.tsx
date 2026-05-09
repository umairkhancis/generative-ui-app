import { CopilotChat } from "@copilotkit/react-core/v2";

const params = new URLSearchParams(window.location.search);
export const agentId = (params.get("agent") as string) || "default";

export default function App() {
    return <CopilotChat agentId={agentId} />;
}
