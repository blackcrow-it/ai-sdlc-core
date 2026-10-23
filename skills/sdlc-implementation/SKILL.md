---
name: sdlc-implementation
description: Implement a scoped software task in a Git worktree with tests, validation and reviewable diffs. Use during feature development and bug fixes.
metadata:
  package: ai-sdlc-core
  version: "2.1.0"
---

# Implementation

**When to use:** Implement a scoped software task in a Git worktree with tests, validation and reviewable diffs. Use during feature development and bug fixes.

## Inputs
Inputs: approved task contract, API/design artifacts, allowed paths.

## Procedure
1. Check repository status and dependencies before editing.
2. Write a focused implementation plan and avoid unrelated refactors.
3. Make incremental changes with security and tests in scope.
4. Run the project's configured `commands` (lint/typecheck/test/e2e) from `.ai-sdlc/project.json` exactly as written.

## Output
Provide changed paths, exact commands, exit codes and a review handoff.

## Safety and quality
- Never claim test passes without running it; do not touch prod or secrets.
- Apply core `policies/permissions.md` and `policies/quality-gates.md` from the `ai-sdlc-core` skill (locate with `sdlc.py where`), plus project rules in `.ai-sdlc/project.json` (commands, coding rules, protected paths).
- Record concrete evidence, issues and handoff per core `references/HANDOFF.md`.
