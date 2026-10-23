---
name: sdlc-code-review
description: Independently review diffs for correctness, architecture, security, tests and maintainability. Use before merge or release.
metadata:
  package: ai-sdlc-core
  version: "2.0.0"
---

# Code Review

**When to use:** Independently review diffs for correctness, architecture, security, tests and maintainability. Use before merge or release.

## Inputs
Inputs: PR/diff, task acceptance criteria, architecture and CI output.

## Procedure
1. Inspect changed code and relevant surrounding behavior; verify diff scope.
2. Flag correctness, auth/security, backwards compatibility and data risks.
3. Check tests and claims against actual CI/check output.
4. Classify findings as blocker/major/minor with file locations and fixes.

## Output
Recommend approve/request-changes with unresolved-risk summary.

## Safety and quality
- Do not approve your own work or bypass required external branch controls.
- Apply core `policies/permissions.md` and `policies/quality-gates.md` from the `ai-sdlc-core` skill (locate with `sdlc.py where`), plus project rules in `.ai-sdlc/project.json` (commands, coding rules, protected paths).
- Record concrete evidence, issues and handoff per core `references/HANDOFF.md`.
