---
name: code-review
description: Independently review diffs for correctness, architecture, security, tests and maintainability. Use before merge or release.
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
- Apply `policies/permissions.md` and `policies/quality-gates.md` (paths relative to repository root).
- Record concrete evidence, issues and handoff per `docs/HANDOFF.md`.
