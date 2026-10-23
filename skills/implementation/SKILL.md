---
name: implementation
description: Implement a scoped software task in a Git worktree with tests, validation and reviewable diffs. Use during feature development and bug fixes.
---

# Implementation

**When to use:** Implement a scoped software task in a Git worktree with tests, validation and reviewable diffs. Use during feature development and bug fixes.

## Inputs
Inputs: approved task contract, API/design artifacts, allowed paths.

## Procedure
1. Check repository status and dependencies before editing.
2. Write a focused implementation plan and avoid unrelated refactors.
3. Make incremental changes with security and tests in scope.
4. Run actual lint/typecheck/unit/integration tests available for the project.

## Output
Provide changed paths, exact commands, exit codes and a review handoff.

## Safety and quality
- Never claim test passes without running it; do not touch prod or secrets.
- Apply `policies/permissions.md` and `policies/quality-gates.md` (paths relative to repository root).
- Record concrete evidence, issues and handoff per `docs/HANDOFF.md`.
