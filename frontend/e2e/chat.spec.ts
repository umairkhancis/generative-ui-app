import { test, expect } from "@playwright/test";
import { openChat, sendMessage, waitForAssistantTurn } from "./helpers";

test("default (LangGraph) agent: hello → response", async ({ page }) => {
  await openChat(page, "default");
  await sendMessage(page, "hello");
  const assistant = await waitForAssistantTurn(page);
  const text = (await assistant.innerText()).trim();
  expect(text.length).toBeGreaterThan(0);
});
