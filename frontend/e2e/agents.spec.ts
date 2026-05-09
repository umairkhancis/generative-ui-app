import { test, expect, Page } from "@playwright/test";

async function askAgent(page: Page, agentId: string, question: string): Promise<string> {
  await page.goto(`http://localhost:5173?agent=${agentId}`);

  const input = page.getByTestId("copilot-chat-textarea");
  await input.waitFor({ state: "visible", timeout: 10_000 });

  await input.fill(question);
  await input.press("Enter");

  await expect(page.getByTestId("copilot-user-message").first()).toBeVisible();

  const loadingCursor = page.getByTestId("copilot-loading-cursor");
  await loadingCursor.waitFor({ state: "visible", timeout: 10_000 });
  await loadingCursor.waitFor({ state: "hidden", timeout: 30_000 });

  const assistantMessage = page.getByTestId("copilot-assistant-message").first();
  await expect(assistantMessage).toBeVisible({ timeout: 5_000 });

  return (await assistantMessage.innerText()).trim();
}

const QUESTION = "What model are you powered by? Please be concise.";

test("LangGraph agent (default) — which model?", async ({ page }) => {
  const response = await askAgent(page, "default", QUESTION);
  console.log(`LangGraph agent: "${response}"`);
  expect(response.length).toBeGreaterThan(0);
});

test("ADK agent (gemini) — which model?", async ({ page }) => {
  const response = await askAgent(page, "gemini", QUESTION);
  console.log(`ADK agent: "${response}"`);
  expect(response.length).toBeGreaterThan(0);
});
