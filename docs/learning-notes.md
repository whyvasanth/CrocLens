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
