import { CopilotRuntime, createCopilotHonoHandler } from "@copilotkit/runtime/v2";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph";
import { serve } from "@hono/node-server";

const LANGGRAPH_DEPLOYMENT_URL = process.env.LANGGRAPH_DEPLOYMENT_URL;
if (!LANGGRAPH_DEPLOYMENT_URL) {
    throw new Error(
        "LANGGRAPH_DEPLOYMENT_URL is not set. Copy frontend/.env.example to frontend/.env, or export the variable in your shell.",
    );
}

const langGraphAgent = new LangGraphHttpAgent({
    url: LANGGRAPH_DEPLOYMENT_URL,
});

const runtime = new CopilotRuntime({
    agents: {
        default: langGraphAgent,
    },
});

const app = createCopilotHonoHandler({
    runtime,
    basePath: "/api/copilotkit",
});

serve({ fetch: app.fetch, port: 4002 }, () => {
    console.log("CopilotKit API server running at http://localhost:4002");
});
