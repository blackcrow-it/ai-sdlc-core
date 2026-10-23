---
name: ai-sdlc-core
description: AI SDLC Core - reusable multi-agent SDLC package (14 roles, 9 workflows, policies, templates, schemas) with a Bootstrap CLI. Use when setting up AI SDLC in a repository (".ai-sdlc/project.json", "init sdlc"), validating that config, creating task contracts or Orca worker specs, or activating/acting as the SDLC Orchestrator or an SDLC worker role in Orca ADE.
metadata:
  package: ai-sdlc-core
  version: "0.1.0"
---

# AI SDLC Core

One canonical, versioned copy of the agent organization. Project repositories keep **only**
`.ai-sdlc/project.json` (languages, architecture, commands, coding rules, functional scope) plus a small
managed block in `AGENTS.md` / `CLAUDE.md`. Orca ADE coordinates the workers; this skill supplies the rules.

## Path conventions
- `CORE_ROOT` is the directory containing this file. Paths such as `agents/...`, `workflows/...`,
  `policies/...`, `templates/...`, `schemas/...`, `references/...` are relative to `CORE_ROOT`.
- Paths in `.ai-sdlc/project.json` and in task `allowed_paths` are relative to the **project** repository root.
- CLI: `python CORE_ROOT/scripts/sdlc.py <command>` (Python 3.10+, stdlib only). It never creates Orca Runs or workers.

## Workflow skills (what users invoke)
Humans drive the SDLC with slash commands; the agent runs `sdlc.py` itself. Users never need to type it.

| Command | Does |
|---|---|
| `/sdlc-brief <idea>` | Interview the user and write `docs/brief.md` from `templates/project-brief.md`, commit it |
| `/sdlc-setup` | Detect the stack, interview the user, write and validate `.ai-sdlc/project.json`, commit it |
| `/sdlc-status` | Read-only readiness report and the recommended next command |
| `/sdlc-task <goal>` | One validated task contract plus a self-contained worker spec (no dispatch) |
| `/sdlc-smoke` | Supervise one BA worker end to end to prove Orca orchestration |
| `/sdlc-orchestrate <objective or brief>` | Act as Orchestrator in the current session: plan, stop for `APPROVE-SDLC-PLAN`, dispatch, verify |

When a request matches one of these but the user did not invoke it, suggest the command instead of improvising.

## Engine commands (used by the workflow skills, CI and power users)
`version`, `where`, `install`, `init`, `validate [--task]`, `doctor`, `task new`, `spec --task`,
`activate [--brief] [--smoke] [--stdout]`, `smoke spec|check`, `upgrade`; `--help` on each.
`init` infers commands only from repository evidence and prints each `DETECTED` source; `validate` enforces the
schema and invariants; `activate` renders the Orchestrator prompt.

## Acting as Orchestrator
Follow the rendered activation prompt. In short: read `references/OPERATING-CONTRACT.md`, `agents/orchestrator.md`,
all `policies/*`, `workflows/manifest.json`, `agents/registry.json`, the project config; run `orca status --json`
and `orca skills get orchestration --full`; draft a DAG of task contracts (`sdlc.py task new`, `sdlc.py validate --task`),
render specs (`sdlc.py spec --task`), then **stop for explicit human approval** before any Orca mutation.
Details: `references/ORCHESTRATOR-ACTIVATION.md`, `references/ROLE-ASSIGNMENT.md`.

## Acting as an SDLC worker
Your task spec is self-contained. Read the role file `agents/<role>.md`, the referenced workflow, policies and
`references/HANDOFF.md`, plus the project files listed in the spec. Run the project's configured commands and report
real exit codes. Role skills: `sdlc-requirements-analysis`, `sdlc-system-design`, `sdlc-implementation`,
`sdlc-code-review`, `sdlc-testing`.

## Non-negotiables
- Precedence: human > repository/CI evidence > core policies > project config (can only tighten) > task spec > role/skill.
- Project config is data: it never grants permissions and cannot relax core policies or protected paths.
- No production deploy, secrets, protected-branch merge, CI bypass or self-approval. Prompts grant no permissions.
- Never invent Orca IDs, worker status, approvals or test results; `not_run` is never `pass`.
