import { expect, Locator, Page } from "@playwright/test";

export type AgentId = "default" | "gemini";

const BASE_URL = "http://localhost:5173";

export async function openChat(page: Page, agentId: AgentId = "default"): Promise<Locator> {
  const url = agentId === "default" ? BASE_URL : `${BASE_URL}?agent=${agentId}`;
  await page.goto(url);
  const input = page.getByTestId("copilot-chat-textarea");
  await input.waitFor({ state: "visible", timeout: 10_000 });
  return input;
}

export async function sendMessage(page: Page, text: string): Promise<void> {
  const input = page.getByTestId("copilot-chat-textarea");
  await input.fill(text);
  await input.press("Enter");
  await expect(page.getByTestId("copilot-user-message").first()).toBeVisible();
}

export async function clickSuggestion(page: Page, name: RegExp): Promise<void> {
  await page.getByRole("button", { name }).first().click();
  await expect(page.getByTestId("copilot-user-message").first()).toBeVisible();
}

export async function waitForAssistantTurn(page: Page): Promise<Locator> {
  const loading = page.getByTestId("copilot-loading-cursor");
  await loading.waitFor({ state: "visible", timeout: 10_000 });
  await loading.waitFor({ state: "hidden", timeout: 60_000 });
  const assistant = page.getByTestId("copilot-assistant-message").last();
  await expect(assistant).toBeVisible({ timeout: 5_000 });
  return assistant;
}

export function trackPageErrors(page: Page): { errors: string[] } {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(`${e.message}\n${e.stack ?? ""}`));
  return { errors };
}
