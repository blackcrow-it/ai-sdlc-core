---
name: sdlc-testing
description: Plan and execute unit, integration, E2E and regression tests tied to acceptance criteria. Use for QA and release validation.
metadata:
  package: ai-sdlc-core
  version: "2.1.0"
---

# Testing

**When to use:** Plan and execute unit, integration, E2E and regression tests tied to acceptance criteria. Use for QA and release validation.

## Inputs
Inputs: acceptance criteria, code revision, test environment.

## Procedure
1. Enumerate test cases for happy path, edges, error and authorization.
2. Choose applicable test level and stable test data; respect scan scope.
3. Run the configured `commands.test`/`commands.e2e` from `.ai-sdlc/project.json`; record environment, command, exit code and evidence.
4. File reproducible defects and identify skipped/unavailable tests distinctly.

## Output
Produce test report with risk-based go/no-go recommendation.

## Safety and quality
- Never replace missing evidence with speculative PASS or test in production by default.
- Apply core `policies/permissions.md` and `policies/quality-gates.md` from the `ai-sdlc-core` skill (locate with `sdlc.py where`), plus project rules in `.ai-sdlc/project.json` (commands, coding rules, protected paths).
- Record concrete evidence, issues and handoff per core `references/HANDOFF.md`.
