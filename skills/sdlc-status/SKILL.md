---
name: sdlc-status
description: Report whether AI SDLC Core and Orca are ready in this repository - installed core and skills, project config, Git baseline, Orca runtime, task contracts, active Run and pending core upgrades - and say what to do next. Use when asked if AI SDLC is set up or what the next SDLC step is.
metadata:
  package: ai-sdlc-core
  version: "0.1.5"
---

Report AI SDLC readiness for the repository at the current working directory. This skill is read-only unless the user approves an upgrade.

1. Locate `<CORE>`: the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`.
2. Run `SDLC doctor`. If it reports the config as missing, recommend /sdlc-setup and stop.
3. List the task contracts from the configured tracker, following the "List" recipe in `<CORE>/references/trackers/<tracker.provider>.md`. Show task_id, owner, status and whether the contract validates, run the graph check (`SDLC validate --task <a> --task <b> ...`), and name the **frontier**: tasks that are `ready` or `changes_requested` with every dependency `accepted`.
4. If the Orca CLI is reachable, run `orca orchestration run-current --json` (read-only) and report the active Run, if any.
5. If the project's `core_version` is older than `SDLC version`, show `SDLC upgrade --dry-run` and run `SDLC upgrade` only after the user approves.
6. Read core `references/DOCUMENTATION-CONTINUITY.md` and the project's documentation map when present. Report
   missing/stale required baselines, unassessed legacy contracts and pending reconciliation tasks as documentation
   gaps, with owners and next steps. Do not infer semantic completeness from schema validation.

Answer in this shape:

- **Status:** READY or BLOCKED.
- **Blockers:** each FAIL with its concrete fix.
- **Warnings:** each WARN, one line each.
- **Next:** one recommended slash command: /sdlc-setup (no config), /sdlc-brief (no `docs/brief.md` and no task contracts yet), /sdlc-smoke (Orca never proven here), `/sdlc-implement <task>` (a frontier task exists), /sdlc-plan (a spec without tasks), /sdlc-orchestrate (a brief or plan to run with Orca workers), or /sdlc-help when the situation fits none of these.
