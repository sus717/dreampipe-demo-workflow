# DreamPipe War Room

## NOW

- Position 1 Product / Pitch: freeze MVP scope, demo script, pitch narrative, judge Q&A.
- Position 2 Creative Director: produce Project Bible and 3-shot storyboard from fixed demo brief.
- Position 3 AI Workflow: implement structured pipeline with mock-first JSON and one real generation path.
- Position 4 Frontend: build Creative Brief UI, pipeline status, shot cards, QA/retry/cost dashboard.
- Position 5 AIGC Integration: test primary image/video model, latency, cost, failure modes, cached fallback assets.

## BLOCKED

- Need Position 3/4 agreement on shared schema field names.
- Need Position 5 confirmation of the fastest stable real generation route.
- Need product reference image or generated packaging placeholder.

## DECISIONS

- Product positioning: AIGC production pipeline, not AI video generator.
- Demo should show process live, not only final video playback.
- Final onsite demo case is fixed: Fuzhou Tourism + Sanfang Qixiang + NiuLai Universe.
- Required demo flow is fixed: input brief -> storyboard -> generation -> QA -> failed-shot retry -> final output.
- MVP is fixed as one product, 15 seconds, 9:16, 3 shots, one video model, one CTA.
- First end-to-end loop can use one forced/reproducible retry.
- Frontend can start from mock JSON immediately.
- Shared schema changes require human confirmation.

## DEMO

Target demo path:

Brief -> Creative Concept -> Project Bible -> 3-shot Storyboard -> Generate -> QA -> Retry Shot 03 -> Final Output.

Demo readiness definition:

- User can enter or load the fixed brief.
- Pipeline states visibly progress.
- At least one shot shows FAIL -> prompt optimization -> regenerated PASS.
- Cost changes after retry.
- Final output screen is present even if media uses cached fallback.

