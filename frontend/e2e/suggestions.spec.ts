import { test, expect } from "@playwright/test";
import { clickSuggestion, openChat, waitForAssistantTurn } from "./helpers";

const SUGGESTIONS = [/show my name/i, /pie chart/i, /flight card/i] as const;

test("suggestion buttons render on initial load", async ({ page }) => {
  await openChat(page);
  for (const name of SUGGESTIONS) {
    await expect(page.getByRole("button", { name })).toBeVisible();
  }
});

test("clicking a suggestion submits the message", async ({ page }) => {
  await openChat(page);
  await clickSuggestion(page, /flight card/i);
  // Suggestions disappear after one is clicked, and an assistant turn begins
  await waitForAssistantTurn(page);
});
