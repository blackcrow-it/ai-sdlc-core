## AI SDLC Core (managed by `sdlc.py`; edit `{{config}}` instead of this block)

This repository is governed by **AI SDLC Core v{{core_version}}** (Agent Skill `ai-sdlc-core`). It stores only
project-specific configuration; roles, workflows, policies, templates and schemas come from the installed core.

- Reply to the user in {{reply_language}} unless asked otherwise; technical artifacts may be in English.
- Project config (languages, architecture, commands, coding rules, functional scope, protected paths): `{{config}}`.
- Operating contract: `references/OPERATING-CONTRACT.md` in the `ai-sdlc-core` skill. Locate the core with
  `python <skills-dir>/ai-sdlc-core/scripts/sdlc.py where` (usual skills dirs: `.claude/skills`, `.agents/skills`,
  `~/.claude/skills`, `~/.agents/skills`).
- Precedence: human instructions > repository/CI evidence > core policies > `{{config}}` (may only tighten core
  policies, never grants permissions) > task spec > core workflow, role and skill files.
- Workflow (`/sdlc-help` maps it): new product `/sdlc-brief` → `/sdlc-orchestrate` (stops for `APPROVE-SDLC-PLAN`);
  feature `/sdlc-grill` → `/sdlc-spec` → `/sdlc-plan` → `/sdlc-implement <task>` per task; one change `/sdlc-task`;
  incoming issues `/sdlc-triage`; readiness `/sdlc-status`; after a session `/sdlc-retro`. Agents run the engine
  `sdlc.py` themselves; workers receive self-contained specs rendered by `sdlc.py spec`.
- Domain language: `GLOSSARY.md` (or `GLOSSARY-MAP.md`) and decisions in `docs/adr/`, created lazily; use their terms.
- Task contracts live only in the tracker named by `tracker` in `{{config}}`; the conventions are in core
  `references/trackers/<provider>.md`. Never keep a second copy elsewhere.
- One task per worker or session. Before reporting done, run the relevant `commands` from `{{config}}` and
  `sdlc.py scope --task <contract>`, and cite real changed paths and exit codes.
