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
  "apps/web/app/api/auth/login/route.ts",
  "apps/web/app/api/auth/logout/route.ts",
  "apps/web/app/api/auth/me/route.ts",
  "apps/web/app/api/auth/signup/route.ts",
  "apps/web/app/api/backend/[...path]/route.ts",
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
  "/api/auth/signup",
  "/api/auth/login",
  "/api/auth/logout",
  "/api/auth/me",
  "/api/v1/portfolio/summary",
  "/api/v1/portfolio/records",
  "/api/v1/portfolio/holdings",
  "/api/v1/portfolio/liabilities",
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
assert.doesNotMatch(authPage, /localStorage/, "Auth page should not store session tokens in localStorage");

const authSharedRoute = read("apps/web/app/api/auth/_shared.ts");
assert.match(authSharedRoute, /httpOnly:\s*true/, "BFF auth route should store the session in an HttpOnly cookie");

const backendProxyRoute = read("apps/web/app/api/backend/[...path]/route.ts");
assert.match(backendProxyRoute, /Authorization: `Bearer \$\{token\}`/, "BFF backend proxy should forward the HttpOnly session token server-side");

const sidebarData = read("apps/web/lib/mock-dashboard-data.ts");
assert.doesNotMatch(sidebarData, /label:\s*"Onboarding"/, "Onboarding should not be a separate primary nav item");

const guidePanel = read("apps/web/components/dashboard/croc-guide-panel.tsx");
assert.doesNotMatch(guidePanel, /backdrop-blur/, "Croc Guide should not blur dashboard content when open");

const dashboardShell = read("apps/web/components/dashboard/dashboard-shell.tsx");
assert.doesNotMatch(dashboardShell, /Good morning, Maya/, "Dashboard greeting should use the signed-in account or portfolio user name");

const sidebar = read("apps/web/components/dashboard/sidebar.tsx");
assert.doesNotMatch(sidebar, /Maya Rivera/, "Sidebar account panel should not be hardcoded to the sample user");

const dataSources = read("docs/data-sources.md");
assert.match(dataSources, /must not require paid providers/i, "Data docs should enforce free-only providers");
assert.match(dataSources, /ambiguous freemium/i, "Data docs should reject ambiguous freemium APIs");

const deploymentDocs = read("docs/aws-deployment.md");
assert.match(deploymentDocs, /Do not deploy to AWS/i, "Deployment docs should block AWS by default");
assert.match(deploymentDocs, /free-only/i, "Deployment docs should preserve the free-only deployment rule");

console.log("CrocLens web smoke tests passed.");
