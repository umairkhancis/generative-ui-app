import { test, expect } from "@playwright/test";
import { AgentId, openChat, sendMessage, waitForAssistantTurn } from "./helpers";

const QUESTION = "What model are you powered by? Please be concise.";

for (const agent of ["default", "gemini"] as AgentId[]) {
  test(`${agent} agent identifies its model`, async ({ page }) => {
    await openChat(page, agent);
    await sendMessage(page, QUESTION);
    const assistant = await waitForAssistantTurn(page);
    const text = (await assistant.innerText()).trim();
    expect(text.length).toBeGreaterThan(0);
  });
}
