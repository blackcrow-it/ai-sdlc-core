---
name: sdlc-implementation
description: Implement exactly one SDLC task contract in its worktree or task branch - test-first at the contract's test seams, inside allowed_paths, with the configured checks, a scope check and a review-ready handoff. Use when a frontend, backend or DevOps task is assigned, during feature development and bug fixes.
metadata:
  package: ai-sdlc-core
  version: "0.1.8"
---

# Implementation

Primary skill of the frontend, backend and DevOps roles. `SDLC` = `python "<CORE>/scripts/sdlc.py"` (locate `<CORE>` with `sdlc.py where`).

Read the assigned role profile and core `references/ROLE-PROFILE-CONTRACT.md`: use the frontend journey/state
checks, backend contract/concurrency checks, DevOps artifact/operation checks, or DB migration checks when a
database implementation contract is assigned. Apply only the relevant checks inside its scope; capabilities
listed by a profile do not authorise infrastructure, production or contract changes.

## One task, one contract

Work from exactly **one** validated task contract: the rendered worker spec in an Orca worker, or the contract loaded by `/sdlc-implement`. Without a contract, stop and ask for one (`/sdlc-task`). Do not start, finish or "help with" any other task, even a sibling in the same plan; report the need instead.

Inside the task:

- write only paths matched by `scope.allowed_paths`; never touch protected paths; never take a forbidden action;
- a change you need outside that ceiling, a new test seam, or an acceptance criterion that looks wrong is a question for the Orchestrator (worker) or the user (session), not a decision you make;
- prefactoring is welcome when it stays inside the ceiling and makes the change easy; a wider refactor is a separate task.

## Procedure

1. **Baseline.** Check `git status`, the branch and the dependencies. Run the configured test command once before editing, so pre-existing failures are known and not blamed on you (record them).
2. **Understand.** Read the contract, the `input_artifacts`, `GLOSSARY.md` and the ADRs in the area. Use glossary terms for names.
   Read core `references/DOCUMENTATION-CONTINUITY.md` and the contract's `documentation` assessment. Confirm
   required baseline updates are accepted before dependent code. Perform this task's owned updates and preserve
   stable requirement IDs; unexpected impacts or missing write scope go to the user/Orchestrator.
3. **Build test-first.** Call the Skill tool with "sdlc-tdd" and work one acceptance criterion at a time, as vertical slices, at the contract's `test_seams`. Run typecheck and the narrowed test command often; keep each red and green run as evidence.
4. **When a check fails and the cause is not obvious**, call the Skill tool with "sdlc-debugging" instead of guessing.
5. **Verify.** Run every `required_checks` entry with the configured commands in `.ai-sdlc/project.json` exactly as written, then the full test suite. Run the scope check (the command in your worker spec, or `SDLC scope --task <contract> --base <base commit>` in a session): it must pass. Map each acceptance criterion to the test that proves it.
6. **Commit** to the task's branch or worktree with `TASK-NNN: <title>`; a bug fix states the confirmed root cause in the body. A pull request body follows core `templates/pull-request.md`. Never merge to a protected branch, force-push or bypass CI.

Before commit/handoff, run `SDLC docs-check --task <contract> --base <recorded base commit>` and report its exit
code plus the canonical requirement → criterion → task → test/evidence links. An empty update list needs a
reviewed explanation; pending sibling documentation tasks remain pending in the handoff.

## Output

Changed paths, commands with exit codes and log paths, the criterion → test map, the scope-check result and a review handoff in the format of core `references/HANDOFF.md` with `next_owner` = the contract's `reviewer_agent`.

## Rules

- Never claim a check passed without running it; `not_run` is never `pass`. Never fabricate exit codes or artifacts.
- No production access, no secrets in code, tests, logs or commits.
- Apply core `policies/permissions.md`, `policies/approval-rules.md` and `policies/quality-gates.md` of the `ai-sdlc-core` skill and the project rules in `.ai-sdlc/project.json` (commands, coding rules, protected paths).
