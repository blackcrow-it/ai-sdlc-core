# AI SDLC Core — source repository instructions

This repository is the **source of AI SDLC Core** — the reusable Agent Skills package under `skills/` and its
Bootstrap CLI. It is itself managed with the core (`.ai-sdlc/project.json`, block below).

## Operating contract
Follow `skills/ai-sdlc-core/references/OPERATING-CONTRACT.md`; it is canonical for every repository that uses the
core, including this one. Reply to the user in Vietnamese unless requested otherwise.

## Maintaining the core
- Canonical content lives only in `skills/ai-sdlc-core/` (agents, workflows, policies, templates, schemas,
  references, assets, scripts) and the `skills/sdlc-*` role skills. Do not reintroduce copies at the repository root.
- One version: bump `version` in `skills/ai-sdlc-core/core.json` and `metadata.version` in every bundled `SKILL.md`
  together; `sdlc.py validate --bundled` enforces it.
- An incompatible change to `schemas/project.schema.json` needs a new `config_schema_version`, an incompatible core
  version bump (minor while 0.x, major from 1.0) and an upgrade note in README "Versioning".
- The Bootstrap CLI is Python 3.10+ standard library only and must never mutate Orca state.
- Before claiming done, run the commands in `.ai-sdlc/project.json` and cite real exit codes:
  `python skills/ai-sdlc-core/scripts/sdlc.py validate --bundled --task examples/task-auth.json` and
  `python -m unittest discover -s tests -v`.

<!-- ai-sdlc-core:begin -->
## AI SDLC Core (managed by `sdlc.py`; edit `.ai-sdlc/project.json` instead of this block)

This repository is governed by **AI SDLC Core v0.1.0** (Agent Skill `ai-sdlc-core`). It stores only
project-specific configuration; roles, workflows, policies, templates and schemas come from the installed core.

- Reply to the user in Vietnamese unless asked otherwise; technical artifacts may be in English.
- Project config (languages, architecture, commands, coding rules, functional scope, protected paths): `.ai-sdlc/project.json`.
- Operating contract: `references/OPERATING-CONTRACT.md` in the `ai-sdlc-core` skill. Locate the core with
  `python <skills-dir>/ai-sdlc-core/scripts/sdlc.py where` (usual skills dirs: `.claude/skills`, `.agents/skills`,
  `~/.claude/skills`, `~/.agents/skills`).
- Precedence: human instructions > repository/CI evidence > core policies > `.ai-sdlc/project.json` (may only tighten core
  policies, never grants permissions) > task spec > core workflow, role and skill files.
- Workflow (`/sdlc-help` maps it): new product `/sdlc-brief` → `/sdlc-orchestrate` (stops for `APPROVE-SDLC-PLAN`);
  feature `/sdlc-grill` → `/sdlc-spec` → `/sdlc-plan` → `/sdlc-implement <task>` per task; one change `/sdlc-task`;
  incoming issues `/sdlc-triage`; readiness `/sdlc-status`; after a session `/sdlc-retro`. Agents run the engine
  `sdlc.py` themselves; workers receive self-contained specs rendered by `sdlc.py spec`.
- Domain language: `GLOSSARY.md` (or `GLOSSARY-MAP.md`) and decisions in `docs/adr/`, created lazily; use their terms.
- Task contracts live only in the tracker named by `tracker` in `.ai-sdlc/project.json`; the conventions are in core
  `references/trackers/<provider>.md`. Never keep a second copy elsewhere.
- One task per worker or session. Before reporting done, run the relevant `commands` from `.ai-sdlc/project.json` and
  `sdlc.py scope --task <contract>`, and cite real changed paths and exit codes.
<!-- ai-sdlc-core:end -->
