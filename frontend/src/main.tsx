import { CopilotKit } from "@copilotkit/react-core/v2";
import "@copilotkit/react-ui/styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { demonstrationCatalog } from "./catalog/demo";
import "./global.css";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <main className="h-screen w-screen">
            <CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint={false} a2ui={{ catalog: demonstrationCatalog }}>
                <App />
            </CopilotKit>
        </main>
    </StrictMode>,
);
