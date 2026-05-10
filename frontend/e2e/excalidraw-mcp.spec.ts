import { test, expect } from "@playwright/test";
import { openChat, sendMessage, trackPageErrors, waitForAssistantTurn } from "./helpers";

test("Excalidraw MCP renders open-ended generative UI in an iframe", async ({ page }) => {
  const { errors } = trackPageErrors(page);
  await openChat(page);

  // Sanity: no iframe before the agent calls Excalidraw
  expect(await page.locator("iframe").count()).toBe(0);

  await sendMessage(
    page,
    "Use the Excalidraw tool to draw a simple flowchart: a Login box with an arrow pointing to a Dashboard box.",
  );
  await waitForAssistantTurn(page);

  // The MCP renderer mounts an iframe and bootstraps the Excalidraw bundle into it
  const iframe = page.locator("iframe").first();
  await expect(iframe).toBeVisible({ timeout: 10_000 });

  // Verify the iframe actually loaded a substantive payload (not an empty shell)
  const measureBody = async () => {
    const handle = await iframe.elementHandle();
    const cf = await handle?.contentFrame();
    if (!cf) return 0;
    return cf.evaluate(() => document.body?.innerHTML.length ?? 0);
  };
  await expect.poll(measureBody, { timeout: 10_000 }).toBeGreaterThan(1000);

  console.log(`Excalidraw iframe body size: ${await measureBody()} bytes`);
  expect(errors).toEqual([]);
});
