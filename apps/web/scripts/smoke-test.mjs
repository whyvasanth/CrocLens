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
  "apps/web/app/login/page.tsx",
  "apps/web/app/signup/page.tsx",
  "apps/web/app/dashboard/page.tsx",
  "apps/web/app/market-news/page.tsx",
  "apps/web/app/tax-planner/page.tsx",
  "apps/web/app/retirement/page.tsx",
  "apps/web/app/journal/page.tsx",
  "apps/web/app/watchlist/page.tsx",
  "apps/web/app/evaluation-metrics/page.tsx",
  "apps/web/app/settings/page.tsx"
];

const requiredDeploymentFiles = [
  ".dockerignore",
  ".env.example",
  "docker-compose.yml",
  "apps/api/Dockerfile",
  "apps/web/Dockerfile"
];

for (const route of requiredRoutes) {
  assertFile(route);
}

for (const file of requiredDeploymentFiles) {
  assertFile(file);
}

const apiClient = read("apps/web/lib/api-client.ts");
const requiredEndpoints = [
  "/api/v1/auth/signup",
  "/api/v1/auth/login",
  "/api/v1/portfolio/summary",
  "/api/v1/ai/chat",
  "/api/v1/ai/action-plan",
  "/api/v1/ai/explain-asset",
  "/api/v1/ai/portfolio-review",
  "/api/v1/data/providers",
  "/api/v1/data/freshness",
  "/api/v1/market/price",
  "/api/v1/market/history",
  "/api/v1/market/indicators",
  "/api/v1/crypto/price",
  "/api/v1/macro/series",
  "/api/v1/rates/treasury",
  "/api/v1/market-news/impact-summary",
  "/api/v1/tax/insights",
  "/api/v1/retirement/plan",
  "/api/v1/journal/entries",
  "/api/v1/watchlist",
  "/api/v1/evaluation/metrics",
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

const evaluationPage = read("apps/web/components/features/evaluation-metrics-page.tsx");
assert.match(evaluationPage, /Evaluation Metrics/, "Evaluation metrics page should render the page title");
assert.match(evaluationPage, /Quality gates/, "Evaluation metrics page should show quality gates");

const authPage = read("apps/web/components/auth/account-auth-page.tsx");
assert.match(authPage, /Create your account/, "Signup page should include account creation");
assert.match(authPage, /onboarding_profile/, "Signup should collect onboarding profile data during account creation");

const sidebarData = read("apps/web/lib/mock-dashboard-data.ts");
assert.doesNotMatch(sidebarData, /label:\s*"Onboarding"/, "Onboarding should not be a separate primary nav item");

const guidePanel = read("apps/web/components/dashboard/croc-guide-panel.tsx");
assert.doesNotMatch(guidePanel, /backdrop-blur/, "Croc Guide should not blur dashboard content when open");

const dashboardShell = read("apps/web/components/dashboard/dashboard-shell.tsx");
assert.match(dashboardShell, /ProviderStatusCard/, "Dashboard should render Phase 21 provider status");
assert.match(dashboardShell, /marketData/, "Dashboard should pass provider market data into Market Snapshot");

const dashboardHook = read("apps/web/hooks/use-dashboard-data.ts");
assert.match(dashboardHook, /getDataProviders/, "Dashboard hook should fetch provider status");
assert.match(dashboardHook, /getMarketPrice/, "Dashboard hook should fetch provider-backed market prices");

const dataSources = read("docs/data-sources.md");
assert.match(dataSources, /must not require paid providers/i, "Data docs should enforce free-only providers");
assert.match(dataSources, /ambiguous freemium/i, "Data docs should reject ambiguous freemium APIs");
assert.match(dataSources, /Phase 21 Provider Layer/, "Data docs should describe Phase 21 provider routing");

const aiAgents = read("docs/ai-agents.md");
assert.match(aiAgents, /Safety Guardrail Agent always runs last/, "AI docs should document safety-last orchestration");

const deploymentDocs = read("docs/aws-deployment.md");
assert.match(deploymentDocs, /Do not deploy to AWS/i, "Deployment docs should block AWS by default");
assert.match(deploymentDocs, /free-only/i, "Deployment docs should preserve the free-only deployment rule");

console.log("CrocLens web smoke tests passed.");
