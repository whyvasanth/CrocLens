import { expect, test } from "@playwright/test";

test("visitor can understand the product and reach demo or signup", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /CrocLens helps you see your money clearly/i })).toBeVisible();
  await expect(page.getByText(/educational information only/i)).toBeVisible();
  await expect(page.getByRole("link", { name: /Try Demo/i })).toHaveAttribute("href", "/dashboard?demo=1");

  await page.getByRole("link", { name: /Create Free Account/i }).first().click();
  await expect(page).toHaveURL(/\/signup$/);
  await expect(page.getByRole("heading", { name: /Build your beginner wealth profile/i })).toBeVisible();
});
