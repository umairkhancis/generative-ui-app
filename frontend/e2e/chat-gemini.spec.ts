import { test, expect } from "@playwright/test";

test("sends hello and gets a response from the gemini agent", async ({ page }) => {
  // Use ?agent=gemini to switch to the Gemini/ADK backend
  await page.goto("http://localhost:5173?agent=gemini");

  // Wait for the chat textarea to be ready
  const input = page.getByTestId("copilot-chat-textarea");
  await input.waitFor({ state: "visible", timeout: 10_000 });

  // Type and send "hello"
  await input.fill("hello");
  await input.press("Enter");

  // User message should appear immediately
  await expect(page.getByTestId("copilot-user-message").first()).toBeVisible();

  // Loading cursor appears while agent is thinking — wait for it to disappear
  const loadingCursor = page.getByTestId("copilot-loading-cursor");
  await loadingCursor.waitFor({ state: "visible", timeout: 10_000 });
  await loadingCursor.waitFor({ state: "hidden", timeout: 30_000 });

  // Assert an assistant message is now visible
  const assistantMessage = page.getByTestId("copilot-assistant-message").first();
  await expect(assistantMessage).toBeVisible({ timeout: 5_000 });

  const text = await assistantMessage.innerText();
  console.log(`Gemini responded: "${text}"`);
  expect(text.trim().length).toBeGreaterThan(0);
});
