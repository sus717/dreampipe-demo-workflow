# DreamPipe Scope

## One-Line Definition

DreamPipe is a controllable, stable, cost-aware AIGC content production pipeline.

## Core Problem

Enterprise AIGC production is blocked by three failures:

1. Consistency failure: characters, scenes, brand style, and tone drift across shots.
2. Quality failure: failed generations require manual diagnosis and prompt repair.
3. Cost failure: retries and high-end models burn budget without routing logic.

## MVP Scope

P0 must be live-demoable:

- Creative Brief input.
- Creative Director output.
- Project Bible generation.
- Storyboard / Shot List generation.
- At least one real image or video generation integration.
- Pipeline status visualization.
- Final output display.

P1 should be shown as a real closed loop if possible:

- AI QA score.
- At least one failed shot retry.
- Prompt optimization before retry.
- Cost dashboard with budget used and remaining.

P2 is optional and must not block P0/P1:

- Multi-model router.
- Multiple style skills.
- NiuLai Hujiu absurd teaser style pack.
- Auto assembly with TTS, BGM, subtitles, and final MP4.

## Recommended Hackathon Cut

Build one stable route:

Creative Brief -> Project Bible -> 3-shot Storyboard -> Generate one or more shots -> QA score -> Retry one shot -> Final Output.

The product claim is the pipeline, not visual perfection.

## Fixed Demo Case

Onsite demo:

- Brand: Fuzhou Tourism
- Experience: Sanfang Qixiang City Walk
- Location: Sanfang Qixiang
- Audience: 18-30
- Platform: Douyin
- Duration: 15 seconds
- Aspect ratio: 9:16
- Budget: RMB 30
- Style: NiuLai Hujiu absurd teaser trailer

Required flow:

Input brief -> storyboard -> generation -> QA -> failed-shot retry -> final output.

## Non-Goals

- Do not compete with foundation models on raw generation quality.
- Do not build a general video editor.
- Do not overbuild multi-model routing before the end-to-end loop works.
- Do not make a demo that only plays a pre-rendered video.
