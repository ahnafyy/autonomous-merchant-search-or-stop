import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("renders the research and package homepage with a working decision tool", async ({ page }, testInfo) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto("/");

  await expect(page.locator("#research-title")).toHaveText("When Should a Shopping Agent Stop Searching?");
  await expect(page.getByText("3,453 SKU clusters", { exact: true })).toBeVisible();
  await expect(page.getByText("40 Shopify decks · 172 seller cards", { exact: true })).toBeVisible();
  await expect(page.getByText(/18,552 retained offer rows from 39 of 48 queries/)).toBeVisible();
  await expect(page.getByText("pip install agentic-shopping-search-or-stop", { exact: true })).toBeVisible();
  await expect(page.getByText("npm install agentic-shopping-search-or-stop", { exact: true })).toBeVisible();
  const paperLink = page.getByRole("link", { name: "Paper", exact: true }).first();
  await expect(paperLink).toBeVisible();
  await expect(paperLink).toHaveAttribute("href", "/paper/");
  await expect(page.getByRole("link", { name: "Product", exact: true })).toHaveCount(0);
  await expect(page.getByText("UCP-PANDORA-REPLAY-001", { exact: true })).toHaveCount(0);

  const interactiveDecision = page.locator("[data-recalled-workbench]");
  await expect(interactiveDecision.getByText("Search again", { exact: true })).toBeVisible();
  await interactiveDecision.getByLabel("Tool/API spend").fill("10.00");
  await expect(interactiveDecision.getByText("Buy now", { exact: true })).toBeVisible();

  const fontFamily = await page.locator("body").evaluate((element) => getComputedStyle(element).fontFamily);
  expect(fontFamily).toContain("Instrument Sans");
  const overflows = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflows).toBe(false);
  expect(consoleErrors).toEqual([]);

  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);
  await page.screenshot({ path: testInfo.outputPath("research-home.png"), fullPage: true });
});

test("keeps research claims on the paper route", async ({ page }, testInfo) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto("/paper/");

  await expect(page.locator("#paper-title")).toHaveText("When Should a Shopping Agent Stop Searching?");
  await expect(page.getByRole("navigation", { name: "Paper navigation" }).getByRole("link", { name: "Overview", exact: true })).toBeVisible();
  await expect(page.getByText("UCP-PANDORA-REPLAY-001", { exact: true })).toBeVisible();
  await expect(page.getByText("UCP-MARKET-RATE-SENSITIVITY-001", { exact: true })).toBeVisible();
  await expect(page.getByText("PANDORA-ADVANTAGE-001", { exact: true })).toBeVisible();
  await expect(page.getByText("SHOPIFY-SELLER-DECK-STUDY-001", { exact: true })).toHaveCount(0);
  await expect(page.getByText("UCP-OBSERVATION-QUALITY-001", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Inconclusive", { exact: true }).first()).toBeVisible();

  const overflows = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflows).toBe(false);
  expect(consoleErrors).toEqual([]);

  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);
  await page.screenshot({ path: testInfo.outputPath("paper.png"), fullPage: true });
});
