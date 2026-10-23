---
name: ai-sdlc-core
description: AI SDLC Core v2 - reusable multi-agent SDLC package (14 roles, 9 workflows, policies, templates, schemas) with a Bootstrap CLI. Use when setting up AI SDLC in a repository (".ai-sdlc/project.json", "init sdlc"), validating that config, creating task contracts or Orca worker specs, or activating/acting as the SDLC Orchestrator or an SDLC worker role in Orca ADE.
metadata:
  package: ai-sdlc-core
  version: "2.0.0"
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

## Bootstrap a new repository (human or agent, from the repository root)
1. `sdlc.py doctor --offline` - confirm the core and the role skills are installed.
2. `sdlc.py init [--test-cmd ...] [--architecture-style ...] [--rule ...] [--in-scope ...]` - writes
   `.ai-sdlc/project.json` from explicit flags plus repository evidence (never guesses commands without evidence),
   adds the managed blocks to `AGENTS.md`/`CLAUDE.md` and ignores `.ai-sdlc/runs/`.
3. Ask the human to complete what init reported as `TODO`/`WARN`, then `sdlc.py validate`.
4. Commit `.ai-sdlc/project.json AGENTS.md CLAUDE.md .gitignore` (Orca worktrees are created from commits).
5. `sdlc.py doctor` (Orca reachable, native `orca-cli`/`orchestration` skills present).
6. `sdlc.py activate [--brief docs/brief.md]` - renders `.ai-sdlc/runs/orchestrator-activation.md`;
   `sdlc.py activate --smoke` renders the one-worker BA smoke test instead.

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
