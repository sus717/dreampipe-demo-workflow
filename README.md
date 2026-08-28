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

Real generation requires `BAILIAN_API_KEY`, configured API URLs in local
`.env`, and a public HTTP(S) product reference image URL. Copy `.env.example`
to an untracked `.env` before local development.
Credentials and private media are never stored in the repository.

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
