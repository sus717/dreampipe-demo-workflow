# pod2-creative-handoff - PLAN

## Goal

- Outcome: Deliver the frozen, model-agnostic Pod 2 creative contracts and 15-second three-shot MVP payloads.
- Non-goals: Do not change Pod 1's Brief, Pod 3's runtime contract, provider prompts, credentials, or generated media.

## Scope

- Write set: Pod 2 shared schemas and payloads, one frontend mock example, and this task record.
- Forbidden: Official Fuzhou Tourism branding, invented beverage assets, model-specific prompt fields, or unstable shot IDs.

## Decisions

| # | Decision | Reason | Date |
|---|----------|--------|------|
| 1 | Keep `project_id` unchanged and shot IDs fixed as S01-S03 | Frozen cross-Pod contract | 2026-08-28 |
| 2 | Allow zero reference assets for now | No approved source assets exist yet | 2026-08-28 |
| 3 | Add explicit dialogue and QA targets to model-agnostic shots | Required for frontend display and downstream compilation/QA | 2026-08-28 |

## Acceptance

| ID | Criterion | Evidence | Status |
|----|-----------|----------|--------|
| AC-001 | Both final payloads validate against Draft 2020-12 schemas | `jsonschema` validator passed both payloads | complete |
| AC-002 | Exactly three stable shots total 15 seconds and contain no provider prompt fields | Contract check passed S01-S03, 15s, 9:16 and forbidden-field scan | complete |
| AC-003 | Frontend mock exposes matching stable IDs, durations, dialogue, continuity and QA fields | Mock contract check passed S01-S03 with 5s each | complete |

## Risks

| Risk | Mitigation | Status |
|------|------------|--------|
| Pod 1 Brief still contains the superseded beverage concept | Do not edit another Pod's file; flag it in handoff | handed off |
| Runtime job schema currently requires at least one asset | Keep shared creative contract valid with an empty array and flag Pod 3 integration work | handed off |
