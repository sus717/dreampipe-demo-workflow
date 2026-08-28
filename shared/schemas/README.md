# DreamPipe Shared Contracts

These are the cross-Pod handoff contracts. Their field names are frozen for the Hackathon unless all human owners agree to a change.

| File | Owner | Consumer | Purpose |
|---|---|---|---|
| `brief.schema.json` | Pod 1 | Pods 2–5 | Campaign scope, user, format, CTA and budget |
| `project_bible.schema.json` | Pod 2 | Pods 3 and 5 | Product, brand and visual invariants |
| `shots.schema.json` | Pod 2 | Pods 3–5 | Model-agnostic storyboard and timing |
| `generation_result.schema.json` | Pods 3 and 5 | Pods 1 and 4 | Per-shot generation status, asset and QA result |

## Handoff from Pod 2 to Pod 3

Pod 2 provides one JSON object that validates against `project_bible.schema.json` and one that validates against `shots.schema.json`.

Pod 3 merges them with Pod 1's approved brief. Pod 3 owns model-specific prompt compilation, generation status, QA/retry and cost; it must not silently change creative intent, visual invariants or shot duration. Any such change returns to Pod 2 for approval.

## Required operating rules

1. `project_id` must be identical in the Project Bible and Shot List. For the MVP, it is exactly the LangGraph `job_id`; this avoids an unnecessary ID-mapping layer.
2. Shot IDs are stable; retrying a shot does not create a new `shot_id`.
3. Product constraints belong in the Project Bible, not repeated as free-form prompt fragments in each shot.
4. The Prompt Compiler may add provider syntax, but must preserve product/brand invariants and all shot-level continuity anchors.
