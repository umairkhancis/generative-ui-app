import { test, expect } from "@playwright/test";
import { openChat, sendMessage, trackPageErrors, waitForAssistantTurn } from "./helpers";

test("showMyName component renders a greeting card", async ({ page }) => {
  const { errors } = trackPageErrors(page);
  await openChat(page);
  await sendMessage(page, "My name is Alice. Please show my name in a card.");
  await waitForAssistantTurn(page);

  // The showMyName render is a div with bg-blue-500 containing "Hi, {name}!"
  const card = page.locator("div.bg-blue-500", { hasText: /^Hi, .+!$/ });
  await expect(card.first()).toBeVisible({ timeout: 5_000 });
  expect(errors).toEqual([]);
});

test("pieChart component renders an SVG pie", async ({ page }) => {
  const { errors } = trackPageErrors(page);
  await openChat(page);
  await sendMessage(
    page,
    "Please show me the distribution of our revenue by category in a pie chart.",
  );
  await waitForAssistantTurn(page);

  // PieChart renders an svg containing one <path fill> per slice
  const slices = page.locator("svg path[fill]");
  await expect.poll(async () => slices.count(), { timeout: 5_000 }).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});

test("flightCard component renders a boarding pass", async ({ page }) => {
  const { errors } = trackPageErrors(page);
  await openChat(page);
  await sendMessage(
    page,
    "Show a flight card for Pacific Air from SFO to JFK departing at 08:30 for $249.",
  );
  await waitForAssistantTurn(page);

  // FlightCard contains the literal "BOARDING PASS" footer text
  await expect(page.getByText("BOARDING PASS").first()).toBeVisible({ timeout: 5_000 });
  expect(errors).toEqual([]);
});
