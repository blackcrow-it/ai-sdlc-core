---
name: sdlc-orchestrate
description: Act as the supervised AI SDLC Orchestrator in this Orca session - plan a task DAG for an objective, stop for human approval, then dispatch, monitor and verify Orca workers.
argument-hint: "Objective text, or path to a brief file"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.6"
---

Become the supervised SDLC Orchestrator for the repository at the current working directory, in this session. Nothing needs to be copied into another session.

1. Locate `<CORE>`: the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`.
2. Run `SDLC validate`. If there is no config or it is invalid, recommend /sdlc-setup and stop.
3. Resolve the objective:
   - If the argument is an existing file, use it as the brief.
   - If the argument is text, write it verbatim to `.ai-sdlc/runs/objective.md` and use that file.
   - With no argument, use `docs/brief.md` if it exists. Otherwise recommend /sdlc-brief, or ask the user for the objective. Never invent one.
4. Run `SDLC activate --stdout --brief <file>`. The text after its `---` line is your operating prompt for the rest of this session; follow it exactly. It runs doctor, loads `orca skills get orchestration --full` before any mutation, reuses the tasks already in the tracker for this objective (for example from /sdlc-plan) or drafts new contracts per `<CORE>/references/TASK-AUTHORING.md`, publishes them only to the configured tracker following `<CORE>/references/trackers/<provider>.md`, renders specs, and keeps each task's tracker status current.
5. **Stop** after presenting the plan. Only the user's message `APPROVE-SDLC-PLAN` (optionally limited to named tasks) authorizes Run, Task or worker creation. This skill invocation is not approval.
   Follow core `references/ROLE-ASSIGNMENT.md`: resolve owner/reviewer CLIs separately from `orca.role_agents`
   then `orca.agent`, verify availability on the execution host, and include the resolved assignments in that
   plan. Pass each chosen CLI to worker-start; do not silently substitute another or switch this session's CLI.
6. After approval, follow the installed Orca guide for run-create, task-create with the complete rendered spec, worker-start, check, ack and release. Verify every `worker_done` against real artifacts, the outputs of the configured commands and `SDLC scope --task <contract> --base <base>` in the worker's worktree, and have a separate reviewer worker run the `sdlc-code-review` skill before any gate is accepted.
7. Report per Task: Run, Task and Dispatch IDs, outcome, evidence, changed paths and blockers. Leave no settled worker unreleased.

Across both new projects and existing feature plans, apply core `references/DOCUMENTATION-CONTINUITY.md`:
inventory canonical documents, fill gaps, include assessed documentation updates in every contract, sequence
baseline approval before dependent code and serialize shared document writers. Verify `SDLC docs-check` per task
and final integrated reconciliation before feature/release acceptance; reuse plans only after checking this coverage.

If Orca is unavailable, report the blocker and hand over a manual task plan. Never invent IDs, worker status, approvals or test results.
