import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(scriptDir, "..", "..", "..");

function read(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

for (const file of [
  "apps/web/app/page.tsx",
  "apps/web/app/dashboard/page.tsx",
  "apps/web/app/assets/[symbol]/page.tsx",
  "apps/web/components/asset-search.tsx",
  "apps/web/components/asset-summary.tsx",
  "apps/web/components/price-chart.tsx",
  "apps/web/components/portfolio-summary.tsx",
  "apps/web/components/croc-guide.tsx",
  "apps/web/lib/api.ts",
  "apps/web/lib/types.ts",
  "apps/api/app/main.py",
  "apps/api/app/market_data.py"
]) {
  assert.equal(existsSync(join(repoRoot, file)), true, `${file} should exist`);
}

const header = read("apps/web/components/app-header.tsx");
const headerLinks = [...header.matchAll(/href="([^"]+)"/g)].map((match) => match[1]).sort();
assert.deepEqual(headerLinks, ["/", "/dashboard"], "Header should only link to active routes");
assert.match(header, /href="\/dashboard"/, "Header should link to the dashboard");

const api = read("apps/web/lib/api.ts");
assert.match(api, /\/api\/quote\//, "Frontend should call the quote endpoint");
assert.match(api, /\/api\/history\//, "Frontend should call the history endpoint");
assert.match(api, /\/api\/demo-portfolio/, "Frontend should call the demo portfolio endpoint");

const guide = read("apps/web/components/croc-guide.tsx");
assert.match(guide, /educational/i, "Croc Guide should show educational framing");
assert.doesNotMatch(guide, /buy this|sell this/i);

console.log("CrocLens simplified smoke tests passed.");
