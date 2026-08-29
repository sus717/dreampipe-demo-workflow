# task-dreampipe-control-tower-ui - PLAN

## Goal

- Outcome: Deliver a polished, runnable DreamPipe control-tower UI using React, TypeScript, Vite 7, MUI, and GSAP.
- Non-goals: Do not implement a backend, mutate pipeline contracts, call paid models, or claim live connectivity.

## Scope

- Write set: `web/**`, root `README.md`, and this task record.
- Forbidden: Existing Python pipeline behavior, shared JSON contracts, credentials, generated media, and the user's current worktree.

## Decisions

| # | Decision | Reason | Date |
|---|----------|--------|------|
| 1 | Build in an isolated worktree from `origin/main` | Preserve the current branch and untracked visual assets | 2026-08-29 |
| 2 | Use deterministic local mock states and label the backend as reserved | The user explicitly requested an empty backend boundary with WebSocket reserved | 2026-08-29 |
| 3 | Use S03 as the visible selective-retry beat | Align the on-stage script and approved visual concept | 2026-08-29 |

## Acceptance

| ID | Criterion | Evidence | Status |
|----|-----------|----------|--------|
| AC-001 | Vite 7 React/TS app renders the production contract, pipeline, selective retry, copilot, preview, and runtime rail | Browser verification passed at 1440x900 and 1280x720 | complete |
| AC-002 | Mock mode supports waiting, running, retrying, and completed states without a backend | 5 unit tests and 2 interactive E2E scenarios passed | complete |
| AC-003 | A typed WebSocket boundary exists but makes no connection without explicit configuration | Unit test passed and UI reads `RESERVED · 未接后端` | complete |
| AC-004 | Typecheck, tests, and production build pass | Typecheck, Vitest, Playwright, Vite build, and diff check passed | complete |

## Risks

| Risk | Mitigation | Status |
|------|------------|--------|
| Dense reference layout becomes unreadable on 1280x720 | Compact breakpoint verified without page overflow or truncated stage labels | mitigated |
| Mock status could be mistaken for a live backend | Persistent `Demo / Mock` and `WebSocket reserved` labels | mitigated |
| Copied concept assets may not yet be approved repository assets | Kept the UI prototype isolated and copied only the four used concept assets | noted |
