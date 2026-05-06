# CrocLens Learning Notes

This document summarizes what each phase teaches.

## Phase 0: Product and System Design Foundation

What we learned:

- Start with product clarity before code.
- Use vertical slices to avoid disconnected frontend, backend, database, and AI work.
- Keep early architecture simple enough to build but structured enough to grow.
- Choose a monorepo for MVP speed and learning.
- Separate frontend, backend, database, AI, and data pipeline responsibilities.
- Treat financial AI output as a safety-critical product surface.
- Track data freshness and limitations from the beginning.
- Avoid AWS cost traps during MVP deployment planning.

Key terms:

- Monorepo: one repository containing multiple parts of the product.
- Vertical slice: a feature built through the UI, API, data model, logic, tests, and docs.
- REST API: an HTTP interface where the frontend asks the backend for data or actions.
- Data freshness: metadata that tells users how current the data is.
- Guardrail: a safety layer that prevents unsafe AI behavior.
- ETL: extract, transform, and load data from sources into the product database.

Practice idea:

- Explain the difference between a frontend responsibility and a backend responsibility using the Portfolio Overview card as an example.

## Phase 1: Frontend Static Dashboard

What we learned:

- A frontend app can be useful before a backend exists if it uses typed mock data.
- Component design keeps UI sections focused and easier to replace later.
- Props are the inputs a component receives from another component.
- State is data that changes while the user interacts with the page, such as the mobile sidebar being open or closed.
- Chart components should receive clean, simple data shapes.
- A static dashboard can still include production habits: accessibility labels, responsive layout, clear empty assumptions, and safety copy.

Key terms:

- Next.js App Router: the modern Next.js routing system based on the `app` folder.
- Component: a reusable UI building block.
- Mock data: fake but realistic data used before real APIs exist.
- Responsive design: layout that adapts to phone, tablet, and desktop screens.
- Client component: a Next.js component that can use browser-only features like state.

Practice idea:

- Add one new mock metric card, then decide whether it belongs in the existing metric row or a separate card.

## Phase 2: Frontend Pages and Navigation

What we learned:

- Next.js App Router maps folders under `app` to URL routes.
- A shared app shell prevents duplicated sidebar and assistant-drawer code across pages.
- Placeholder pages are useful when they clarify future product intent instead of pretending features are finished.
- Navigation should use real links, active states, and route-aware behavior.
- Route structure is a product architecture decision because URLs shape how users and engineers understand the app.

Key terms:

- Route: a URL path that renders a page.
- Redirect: automatically sending one URL to another, such as `/` to `/dashboard`.
- App shell: reusable layout chrome around pages, such as sidebar, main surface, and assistant drawer.
- Active state: visual feedback showing which page the user is on.
- Placeholder page: a deliberately incomplete page that explains what will be built later.

Practice idea:

- Pick one placeholder page and write the API endpoint you think it will need in a later phase.

## Phase 3: Backend API Skeleton

What we learned:

- FastAPI lets us define HTTP endpoints with Python functions.
- Pydantic models act as API contracts by validating request and response shapes.
- Routers keep API areas separated, such as portfolio, assets, action plans, and AI.
- Service functions keep business/mock logic out of route handlers.
- Mock APIs help the frontend and backend agree on contracts before the database exists.
- AI responses should include safety fields from the first backend version.

Key terms:

- Endpoint: a URL plus HTTP method, such as `GET /health`.
- Request model: the expected shape of incoming JSON.
- Response model: the expected shape of outgoing JSON.
- Validation: checking that data matches the expected type and rules.
- Status code: a numeric HTTP result such as `200`, `404`, or `422`.
- Router: a group of related endpoints.

Practice idea:

- Add one new mock endpoint idea for liabilities, then write the response fields it should return.

## Phase 4: Database Design

What we learned:

- A relational database stores related data in tables connected by keys.
- SQLAlchemy models let Python code describe database tables.
- Alembic migrations version database changes so every environment can apply the same schema.
- Primary keys uniquely identify rows.
- Foreign keys connect rows across tables.
- Indexes make common queries faster, but should be chosen intentionally.
- Assets and holdings should be separate because an asset describes what something is, while a holding describes what a user owns.

Key terms:

- Table: a structured collection of rows.
- Row: one record in a table.
- Primary key: the unique ID for one row.
- Foreign key: a column that points to a row in another table.
- Index: a database structure that speeds up lookup queries.
- Migration: a versioned schema change.
- ORM: object-relational mapper, a tool that maps Python classes to database tables.

Practice idea:

- Pick one table and explain which user workflow will create a row in that table.

## Phase 5: Frontend-Backend Integration

What we learned:

- A frontend API client centralizes how the UI talks to the backend.
- TypeScript response types mirror backend Pydantic response models.
- Loading states tell users that data is being fetched.
- Error states tell users what went wrong and how to recover.
- Client-server integration should preserve clear data contracts instead of scattering fetch calls through every component.
- Not every dashboard card needs to be API-backed at once; integration can move one contract at a time.

Key terms:

- API client: a small module that wraps HTTP calls to the backend.
- Data contract: the agreed request/response shape between frontend and backend.
- Loading state: UI shown while a request is in progress.
- Error state: UI shown when a request fails.
- Retry: letting the user or UI try the request again.
- Environment variable: configuration passed into the app without hardcoding values.

Practice idea:

- Add one more frontend API call to a placeholder page, such as loading `/api/v1/assets` on the Portfolio page.

## Phase 6: Portfolio and Cross-Asset Logic

What we learned:

- Business logic should live in testable service functions, not route handlers.
- Transparent formulas are easier to explain, debug, and improve.
- Weighted averages are useful when larger holdings should influence a score more than smaller holdings.
- Diversification needs a different formula because it depends on concentration and number of asset classes.
- Not every score is good/bad. Tax complexity is a signal that more tracking may be needed.
- Frontend scorecards should show explanations and formulas when the product is beginner-first.

Key terms:

- Business logic: the rules that calculate product behavior.
- Weighted average: an average where larger or more important items count more.
- Heuristic: a practical rule of thumb, not a perfect model.
- Concentration: when one asset or asset class is a large share of the portfolio.
- Auditability: being able to explain how a result was produced.

Practice idea:

- Change one asset-class weight in `portfolio_calculations.py`, run the tests, and explain which score changed.

## Phase 7: Asset Detail Pages

What we learned:

- A detail page should be driven by an API contract, not hardcoded UI text.
- Dynamic routes let one frontend page render many records, such as `/assets/asset_btc`.
- Portfolio pages can become navigation surfaces that link users into deeper workflows.
- Beginner-first finance products need plain-language sections for risk, liquidity, taxes, income potential, and what to watch.
- Financial safety is part of the response model: confidence, data limitations, sources, and educational disclaimers travel with the data.

Key terms:

- Dynamic route: a URL pattern where part of the path is a variable, such as `[assetId]`.
- Detail endpoint: an API endpoint that returns one rich record instead of a list.
- Data contract: the response shape that backend and frontend agree to share.
- Guardrail field: structured safety metadata such as disclaimers, limitations, and confidence.

Practice idea:

- Add a cash detail page to the Phase 7 sample data, then confirm it appears on `/portfolio` and opens from its own `/assets/...` route.

## Phase 8: User Onboarding and Risk Profile

What we learned:

- Onboarding is product context, not just a form.
- Structured onboarding answers can later personalize dashboards, action plans, and AI prompts.
- Risk profiles should be transparent heuristics in the MVP, not hidden black-box scores.
- Frontend forms need typed request objects so the backend receives predictable data.
- Financial onboarding should use safe educational wording and return confidence and limitations.

Key terms:

- Personalization context: user-provided information that changes what the product emphasizes.
- Controlled form: a React form where component state owns each input value.
- Heuristic risk score: a simple rule-based score that is easy to explain and audit.
- Form validation: checking that submitted fields match allowed values and ranges.

Practice idea:

- Add one more onboarding field for monthly savings rate, then update the backend risk scoring notes to use it.

## Phase 9: AI Assistant v1

What we learned:

- A safe AI feature can start rule-based before using an external LLM.
- Intent routing decides what kind of question the user is asking.
- Prompt context is the structured package of rules, user question, and app context that a future LLM would receive.
- Guardrails should run before returning financial assistant output.
- The frontend should render assistant confidence, limitations, sources, and safety state instead of only chat text.

Key terms:

- Intent routing: classifying a user question into a category such as debt, tax, risk, or market.
- Prompt context: structured input prepared for a future model call.
- Guardrail: logic that detects or rewrites unsafe requests.
- Prompt version: a label that helps track which prompt structure produced an answer.

Practice idea:

- Add one new intent for real estate questions, then write a test that proves mortgage and home-equity wording routes correctly.

## Phase 10: Multi-Agent Architecture

What we learned:

- Multi-agent architecture is mainly about decomposing work into clear roles and traceable handoffs.
- A deterministic orchestrator is a good first step before adding LangGraph or model-backed agents.
- Agent state should be explicit: user question, intent, specialist output, action-plan output, and safety review.
- Tool use should be visible in traces so engineers and users can audit how an answer was produced.
- Stubbed agents are useful when they clarify future architecture without pretending the feature is complete.

Key terms:

- Orchestrator: the coordinator that decides which agents run and in what order.
- Agent registry: the list of available agents, their roles, and implementation status.
- Agent trace: an ordered explanation of which agents handled a request.
- Handoff: passing state or output from one agent to another.
- Tool use: when an agent reads structured data, such as portfolio summary or liability summary.

Practice idea:

- Add a real estate intent mapping that routes home-equity questions to the Real Estate Insight Agent, then show that trace in Croc Guide.

## Phase 11: Data Engineering Pipeline

What we learned:

- A data pipeline turns external or file-based data into a validated product-ready shape.
- ETL means extract, transform, and load.
- Pydantic can validate data files the same way it validates API responses.
- Freshness and lineage metadata help users understand whether data is current and where it came from.
- Data quality checks should run before market data reaches dashboards or AI agents.
- Free APIs are useful for MVP learning, but production systems need caching, retries, rate-limit handling, and graceful failure behavior.

Key terms:

- Extract: read data from a file, API, database, or stream.
- Transform: clean and normalize data into the internal CrocLens shape.
- Load: save or expose the transformed data for the app to use.
- Lineage: metadata describing where data came from.
- Freshness: metadata describing how current the data is.
- Rate limit: a provider rule limiting how many API calls can be made.
- Cache: stored data reused to reduce repeated provider calls.

Practice idea:

- Add a sample bond ETF record to `apps/api/data/sample_market_data.json`, then update the test count and run the API tests.

## Phase 12: Market, News, And Personal Impact

What we learned:

- News should be mapped to portfolio context before it reaches the user.
- "How does this affect me?" is an impact explanation, not a trading signal.
- Safe product design means showing confidence, limitations, and sources next to market commentary.
- A deterministic sample workflow is easier to test than live news ingestion.

Key terms:

- Impact mapping: connecting a headline or market event to affected holdings.
- Exposure: the part of a portfolio that may be touched by a risk or event.
- Source limitation: a clear statement of what the data cannot tell the user.

Practice idea:

- Add one inflation article and map it to cash, real estate, and retirement holdings.

## Phase 13: Tax-Aware Module

What we learned:

- A tax lot is a purchase record used to reason about cost basis and holding period.
- Unrealized gains and losses are educational signals until a taxable transaction occurs.
- Holding period labels can help beginners understand short-term versus long-term treatment.
- Tax-loss harvesting explanations must include wash-sale warnings and professional-review language.

Key terms:

- Cost basis: what the user paid for a lot, including relevant adjustments.
- Unrealized gain/loss: value change before a sale.
- Holding period: how long the lot has been held.
- Wash sale: a rule that can limit loss deductions after certain replacement purchases.

Practice idea:

- Add one more sample tax lot and confirm the API labels it short-term or long-term.
