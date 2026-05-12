import { CopilotRuntime, createCopilotHonoHandler } from "@copilotkit/runtime/v2";
import { HttpAgent } from "@ag-ui/client";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph";
import { serve } from "@hono/node-server";

const langGraphAgent = new LangGraphHttpAgent({
    url: process.env.LANGGRAPH_DEPLOYMENT_URL || "http://localhost:8000",
});

const adkAgent = new HttpAgent({
    url: process.env.ADK_AGENT_URL || "http://localhost:8009",
});

const runtime = new CopilotRuntime({
    agents: {
        default: langGraphAgent,
        gemini: adkAgent,
    },
    a2ui: { injectA2UITool: true },
    mcpApps: {
        servers: [
            {
                type: "http",
                url: "https://mcp.excalidraw.com",
                serverId: "example_mcp_server", // com.excalidraw.mcp
            },
            {
                type: "http",
                url: "https://certainly-occur-permit-joyce.trycloudflare.com/mcp",
                serverId: "elli_example_mcp_server",
            },
        ],
    },
});

const app = createCopilotHonoHandler({
    runtime,
    basePath: "/api/copilotkit",
});

serve({ fetch: app.fetch, port: 4002 }, () => {
    console.log("CopilotKit API server running at http://localhost:4002");
});
