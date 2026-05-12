import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:5173";

test("Todos button is visible on load", async ({ page }) => {
  await page.goto(BASE_URL);

  const todosBtn = page.getByRole("button", { name: "Todos" });
  await todosBtn.waitFor({ state: "visible", timeout: 10_000 });
  await expect(todosBtn).toBeVisible();
});

test("Todos button opens the panel and disappears", async ({ page }) => {
  await page.goto(BASE_URL);

  const todosBtn = page.getByRole("button", { name: "Todos" });
  await todosBtn.waitFor({ state: "visible", timeout: 10_000 });
  // cpk-web-inspector overlays the page in dev — force the click past it
  await todosBtn.click({ force: true });

  // Button should disappear once panel is open
  await expect(todosBtn).not.toBeVisible();

  // Panel should appear (desktop: aside)
  const panel = page.locator("aside").first();
  await expect(panel).toBeVisible();
});
