# kaiwu_hackathon

Project development notes belong here.

## Development Commands

Record the real project commands after bootstrap:

```bash
# Install dependencies
# e.g. npm install

# Run locally
# e.g. npm run dev

# Run tests
# e.g. npm test

# Build
# e.g. npm run build
```

Replace the examples with the real commands discovered from this project. If a command is unknown, record the open question in `Harness/tasks/<task-id>/PROGRESS.md`.

## DreamPipe Pipeline (Pod 3)

The repository includes a LangGraph pipeline under `src/dreampipe/`. It supports
the zero-cost Mock flow and an explicit Alibaba Cloud Bailian
`happyhorse-1.1-i2v` provider adapter. Workflow documentation is in
[`docs/workflows/`](docs/workflows/), including the Pod 2 creative handoff and
the Pod 4 frontend status contract.

Run the Mock flow with:

```powershell
$env:PYTHONPATH = ".venv_lib;src"
python scripts/run_pipeline.py shared/brief.json --provider mock
```

默认读取 `shared/project_bible.json` 与 `shared/shots.json` 作为 Pod 2 冻结的模型无关创意合同，
并用 GLM-4.5-Air 编译模型专用 Prompt：

```powershell
python scripts/run_pipeline.py shared/brief.json --provider happyhorse `
  --reference-image-url https://your-cdn.example.com/reference.png `
  --creative-source pod2 --llm glm
```

没有真实、可访问的参考图时，Pipeline 返回 `WAITING_FOR_ASSETS`，不会生成 Mock 视频、QA 或合成成片。
`--creative-source mock` 与 `--llm mock` 仅用于本地回归；演示和生产路径使用默认的 `pod2` 与 `glm`。

Real generation requires `BAILIAN_API_KEY`, configured API URLs in local
`.env`, and a public HTTP(S) product reference image URL. Copy `.env.example`
to an untracked `.env` before local development.
Credentials and private media are never stored in the repository.

## DreamPipe Web Control Tower

The frontend prototype lives in `web/` and uses React, TypeScript, Vite 7,
MUI, and GSAP. It runs against deterministic local demo states while the
backend is unavailable. The WebSocket boundary is reserved but inert unless
`VITE_PIPELINE_WS_URL` is explicitly configured.

```bash
cd web
npm install
npm run dev
```

Validation commands:

```bash
cd web
npm run typecheck
npm test
npm run build
```

## Git And Release Notes

- Keep branch, commit, pull request, CI, and release conventions in this README.
- Do not place build scripts, git policy, or project maintenance instructions in `CLAUDE.md`.
- Keep code architecture notes in `Harness/project/architecture.md` or feature docs.
- For README improvements, use `.claude/skills/wf-readme/SKILL.md`; preserve public docs unless a rewrite is approved.

## Harness

The agentic engineering harness lives in `Harness/`.

- Normal agent sessions start from `CLAUDE.md`.
- Use `Harness/specs/guides/SETUP.md` only for install/bootstrap guidance, migration, upgrade decisions, or explicit setup requests.
- Use `Harness/README.md` as the Harness workflow router when a routed task needs it.
- Load memory and resource registrations from `Harness/MEMORY.md` only when routed.
- Track active work in `Harness/PROGRESS.md` and `Harness/tasks/<task-id>/PROGRESS.md`.
- Use `/wf-update` or `$wf-update` for Harness upgrades; the agent should report version, changed files, validation results, and release highlights from update metadata.
- Use `Harness/specs/workflows/WF.md` only when the user explicitly invokes a WF command such as `/wf` or `/wf-max`; complex work may still use direct planning, tests, and subagents without entering WF.
  - Claude Code: invoke the `wf` skill with `/wf`.
  - Codex: invoke the `wf` skill with `$wf` or `/skills`.
- Use `Harness/specs/runtime/subagents.md` when coordinating multiple agents.

Tool discovery files stay at the repository root:

- Claude Code: `.claude/settings.json`, `.claude/agents/`, and `.claude/skills/`.
- Codex: `.agents/skills/` for repo skills and `.codex/` for config placeholders. The bundled update reminder uses a startup-only hook; avoid turn-by-turn runtime hooks unless `/wf-auto` explicitly opts into a bounded tick hook.
