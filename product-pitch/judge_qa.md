# Judge Q&A

## Q1: Is this just calling several model APIs?

No. Model APIs solve single-step generation. DreamPipe solves production orchestration: shared project constraints, structured shot planning, QA scoring, prompt repair, retry strategy, and cost tracking.

## Q2: What is technically difficult here?

The hard part is keeping state and constraints coherent across a multi-step creative pipeline. Each stage must preserve the same Project Bible, produce structured outputs, and feed QA/retry decisions back into generation without breaking the pipeline contract.

## Q3: Why would users not just use Runway, Kling, Seedance, or Veo directly?

Those tools are strong generators. DreamPipe is the layer that helps teams decide what to generate, keep it consistent, inspect failures, retry selectively, and manage budget. It can route to those models instead of replacing them.

## Q4: What is the MVP proof?

A live brief can produce a Project Bible, storyboard, generation tasks, QA scores, a failed-shot diagnosis, a repaired prompt, a selective retry, and a final output view.

## Q5: What is the business model?

Likely options:

- SaaS workflow for marketing and brand teams.
- Usage-based pipeline orchestration fee on top of model costs.
- Enterprise brand-skill setup and managed templates.

## Q6: What is the biggest risk?

Real model latency and output instability during live demo. Mitigation: keep planning, QA, retry, and cost UI live; cache generated media from prior pipeline runs as fallback.

## Q7: How do you measure quality?

Use a QA score composed from prompt alignment, visual quality, style consistency, character/location consistency, and brand compliance. For hackathon MVP, at least one category-level failure reason must drive a retry prompt.

## Q8: Why is NiuLai Universe relevant?

It proves style skills are pluggable. The same pipeline can produce tourism, corporate, cinematic, social viral, or a custom showcase style without changing the orchestration logic.

## Q9: What would you build next after the hackathon?

Production-grade model adapters, brand asset ingestion, stronger vision QA, cost/quality optimization, team review workflow, and repeatable campaign templates.

## Q10: What if QA is wrong?

QA is not treated as absolute truth. It is a control signal. Human review can override it, and repeated production data can improve scoring thresholds.

