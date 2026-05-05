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
