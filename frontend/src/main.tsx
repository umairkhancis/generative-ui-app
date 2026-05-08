import { CopilotKit } from "@copilotkit/react-core/v2";
import "@copilotkit/react-ui/styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./globals.css";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <main className="h-screen w-screen">
            <CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint={false}>
                <App />
            </CopilotKit>
        </main>
    </StrictMode>,
);
