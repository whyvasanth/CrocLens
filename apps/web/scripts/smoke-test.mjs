import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const webRoot = join(scriptDir, "..");
const repoRoot = join(webRoot, "..", "..");

function read(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

function assertFile(relativePath) {
  assert.equal(existsSync(join(repoRoot, relativePath)), true, `${relativePath} should exist`);
}

const requiredRoutes = [
  "apps/web/app/dashboard/page.tsx",
  "apps/web/app/market-news/page.tsx",
  "apps/web/app/tax-planner/page.tsx",
  "apps/web/app/retirement/page.tsx",
  "apps/web/app/journal/page.tsx",
  "apps/web/app/watchlist/page.tsx",
  "apps/web/app/settings/page.tsx"
];

for (const route of requiredRoutes) {
  assertFile(route);
}

const apiClient = read("apps/web/lib/api-client.ts");
const requiredEndpoints = [
  "/api/v1/portfolio/summary",
  "/api/v1/market-news/impact-summary",
  "/api/v1/tax/insights",
  "/api/v1/retirement/plan",
  "/api/v1/journal/entries",
  "/api/v1/watchlist",
  "/api/v1/security/status",
  "/api/v1/privacy/settings",
  "/api/v1/privacy/export",
  "/api/v1/privacy/data"
];

for (const endpoint of requiredEndpoints) {
  assert.match(apiClient, new RegExp(endpoint.replaceAll("/", "\\/")), `${endpoint} should be wired in api-client.ts`);
}

const settingsPage = read("apps/web/components/features/settings-privacy-page.tsx");
assert.match(settingsPage, /Export preview/, "Settings page should include export preview");
assert.match(settingsPage, /Delete preview/, "Settings page should include delete preview");

const dataSources = read("docs/data-sources.md");
assert.match(dataSources, /must not require paid providers/i, "Data docs should enforce free-only providers");
assert.match(dataSources, /ambiguous freemium/i, "Data docs should reject ambiguous freemium APIs");

console.log("CrocLens web smoke tests passed.");
