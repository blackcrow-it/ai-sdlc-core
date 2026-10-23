---
name: sdlc-status
description: Report whether AI SDLC Core and Orca are ready in this repository - installed core and skills, project config, Git baseline, Orca runtime, task contracts, active Run and pending core upgrades - and say what to do next. Use when asked if AI SDLC is set up or what the next SDLC step is.
metadata:
  package: ai-sdlc-core
  version: "0.1.0"
---

Report AI SDLC readiness for the repository at the current working directory. This skill is read-only unless the user approves an upgrade.

1. Locate `<CORE>`: the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`.
2. Run `SDLC doctor`. If it reports the config as missing, recommend /sdlc-setup and stop.
3. List `.ai-sdlc/tasks/*.json` with task_id, owner, status and whether `SDLC validate --task <file>` passes.
4. If the Orca CLI is reachable, run `orca orchestration run-current --json` (read-only) and report the active Run, if any.
5. If the project's `core_version` is older than `SDLC version`, show `SDLC upgrade --dry-run` and run `SDLC upgrade` only after the user approves.

Answer in this shape:

- **Status:** READY or BLOCKED.
- **Blockers:** each FAIL with its concrete fix.
- **Warnings:** each WARN, one line each.
- **Next:** one recommended slash command: /sdlc-brief (no `docs/brief.md` and no task contracts yet), /sdlc-setup, /sdlc-smoke, /sdlc-task or /sdlc-orchestrate.
