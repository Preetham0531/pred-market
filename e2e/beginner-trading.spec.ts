import { expect, test } from "@playwright/test";

test("markets-first home and responsive search", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Markets" })).toBeVisible();
  await expect(page.getByText("Simulated funds").last()).toBeVisible();
  await expect(page.getByRole("link", { name: /Will a frontier AI lab/ })).toBeVisible();
  await expect(page.getByText("Suggest", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Live", { exact: true })).toHaveCount(0);

  await page.getByRole("button", { name: "Search markets" }).click();
  const search = page.getByPlaceholder("Search markets");
  await expect(search).toBeVisible();
  await search.fill("frontier");
  await expect(page.getByRole("link", { name: /frontier AI lab/ }).first()).toBeVisible();

  const searchBox = await search.boundingBox();
  const triggerBox = await page.getByRole("button", { name: "Search markets" }).boundingBox();
  if (testInfo.project.name !== "mobile") {
    expect(searchBox?.y).toBeGreaterThan(triggerBox?.y ?? 0);
  } else {
    const sheetBox = await page.getByRole("dialog", { name: "Search markets" }).boundingBox();
    expect(sheetBox?.x).toBeLessThan(2);
    expect(sheetBox?.width).toBeGreaterThan(380);
  }
});

test("signup, funding, trading, cancellation, live depth, and polling fallback", async ({ page, browser }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "Trading workflow runs once on desktop.");
  const email = `qa-${Date.now()}@predmarket.dev`;

  await page.goto("/sign-up");
  await page.getByLabel("Display name").fill("QA Trader");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("StrongPass123");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL("/");

  await page.goto("/markets/ai-model-release");
  await expect(page.getByRole("heading", { name: "Order book" })).toBeVisible();

  const liveContext = await browser.newContext();
  const liveObserver = await liveContext.newPage();
  await liveObserver.goto("/markets/ai-model-release");
  const liveBestNo = liveObserver.locator('[aria-label^="NO bids price"]').first();
  const liveBefore = await liveBestNo.getAttribute("aria-label");

  const fallbackContext = await browser.newContext();
  const fallbackObserver = await fallbackContext.newPage();
  await fallbackObserver.routeWebSocket(/\/ws\/v1/, (socket) => socket.close());
  await fallbackObserver.goto("/markets/ai-model-release");
  const fallbackBestNo = fallbackObserver.locator('[aria-label^="NO bids price"]').first();
  const fallbackBefore = await fallbackBestNo.getAttribute("aria-label");

  await page.getByRole("button", { name: "Add funds" }).click();
  await page.getByLabel("Amount").fill("10000");
  await page.getByRole("button", { name: "Add and continue" }).click();
  await expect(page.getByText("Confirm your first trade")).toBeVisible();
  await page.getByRole("button", { name: "Confirm trade" }).click();
  await expect(page.getByText("Trade completed")).toBeVisible();
  await expect.poll(() => liveBestNo.getAttribute("aria-label"), { timeout: 4000 }).not.toBe(liveBefore);
  await expect.poll(() => fallbackBestNo.getAttribute("aria-label"), { timeout: 8000 }).not.toBe(fallbackBefore);

  await page.getByRole("button", { name: "Advanced limit order" }).click();
  await page.getByLabel("Limit price").fill("1");
  await page.getByRole("textbox", { name: "Quantity", exact: true }).fill("1");
  await page.getByRole("button", { name: "Place limit order" }).click();
  await expect(page.getByText("Waiting for another order")).toBeVisible();
  await page.getByRole("link", { name: "View or cancel" }).click();
  await expect(page).toHaveURL("/orders");
  await page.getByRole("button", { name: "Cancel", exact: true }).first().click();
  await expect(page.getByText(/was cancelled and unused funds were released/)).toBeVisible();
  await liveContext.close();
  await fallbackContext.close();
});
