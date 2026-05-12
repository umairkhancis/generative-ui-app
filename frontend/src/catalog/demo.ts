import { createCatalog } from "@copilotkit/a2ui-renderer";
import { demonstrationCatalogDefinitions } from "./definitions";
import { demonstrationCatalogRenderers } from "./renderers";

export const demonstrationCatalog = createCatalog(
    demonstrationCatalogDefinitions,
    demonstrationCatalogRenderers,
    {
        catalogId: "copilotkit://app-dashboard-catalog",
        includeBasicCatalog: false,
    },
);
