import { CopilotKit } from "@copilotkit/react-core/v2";
import "@copilotkit/react-ui/styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { demonstrationCatalog } from "./catalog/demo";
import "./global.css";
import { ErrorBoundary } from "./error-boundary";
import App from "./App";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <ErrorBoundary>
            <CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint={false} a2ui={{ catalog: demonstrationCatalog }}>
                <App />
            </CopilotKit>
        </ErrorBoundary>
    </StrictMode>,
);
