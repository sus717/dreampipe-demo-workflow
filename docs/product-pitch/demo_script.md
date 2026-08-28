# 3-Minute Demo Script

## Demo Goal

Judges should remember: DreamPipe does not just generate a video; it generates a controlled production process for making videos.

## Fixed Team Decision

The onsite demo case is fixed:

Fuzhou Tourism + Sanfang Qixiang + NiuLai Hujiu absurd teaser trailer.

The flow must run through:

Input brief -> storyboard -> generation -> QA -> failed-shot retry -> final output.

## Setup

Use this fixed live brief:

- Brand: Fuzhou Tourism
- Experience: Sanfang Qixiang City Walk
- Location: Sanfang Qixiang
- Audience: 18-30
- Platform: Douyin
- Duration: 15 seconds
- Aspect ratio: 9:16
- Budget: RMB 30
- Style: NiuLai Hujiu absurd teaser trailer

## Timeline

### 0:00-0:20 Opening

"Most AIGC demos show a final video. DreamPipe shows the production line behind it. The problem is not whether AI can generate something impressive once. The problem is whether teams can generate brand-safe, consistent, cost-controlled content repeatedly."

### 0:20-0:45 Input Brief

Show the Creative Brief form.

Say:
"We enter a real campaign brief: Fuzhou Tourism, Sanfang Qixiang, young Douyin audience, 15 seconds, RMB 30 budget, NiuLai Hujiu absurd teaser style."

Click `Generate`.

### 0:45-1:20 Planning Layer

Show pipeline status:

- Brief Parsed
- Creative Concept
- Project Bible
- Storyboard

Say:
"Before generating pixels, DreamPipe creates a Project Bible. This locks character, location, visual style, brand rules, and tone. Every shot reads from the same source of truth."

### 1:20-2:10 Generation + QA

Show shot cards with generation status and QA scores.

Required demo beat:

- Shot 01 PASS, QA 88
- Shot 02 PASS, QA 84
- Shot 03 FAIL, QA 64, reason: character or style mismatch
- Shot 03 retry prompt generated
- Shot 03 regenerated, QA 87, PASS

Say:
"When a shot fails, we do not throw away the whole production. DreamPipe identifies the reason, repairs the prompt, retries only the failed shot, and tracks cost."

### 2:10-2:40 Cost + Output

Show cost dashboard:

- Budget: RMB 30
- Used: simulated or real value
- Retry cost isolated
- Final output ready

Say:
"This is what production teams need: not one lucky generation, but controlled iteration inside a budget."

### 2:40-3:00 Closing

Play final output or show generated result grid.

Say:
"DreamPipe is the orchestration layer above AIGC models: Consistent, Controllable, Cost-efficient. The work is not just the video. The work is the machine that produces the video."

## Fallback Demo

If real generation is unstable, keep the live pipeline interaction real and switch only final media to cached assets. State clearly:

"For time stability, this final preview uses cached assets from the same pipeline run. The planning, QA, retry, and cost state are live."
