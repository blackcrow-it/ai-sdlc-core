---
name: testing
description: Plan and execute unit, integration, E2E and regression tests tied to acceptance criteria. Use for QA and release validation.
---

# Testing

**When to use:** Plan and execute unit, integration, E2E and regression tests tied to acceptance criteria. Use for QA and release validation.

## Inputs
Inputs: acceptance criteria, code revision, test environment.

## Procedure
1. Enumerate test cases for happy path, edges, error and authorization.
2. Choose applicable test level and stable test data; respect scan scope.
3. Run automated checks; record environment, command, exit code and evidence.
4. File reproducible defects and identify skipped/unavailable tests distinctly.

## Output
Produce test report with risk-based go/no-go recommendation.

## Safety and quality
- Never replace missing evidence with speculative PASS or test in production by default.
- Apply `policies/permissions.md` and `policies/quality-gates.md` (paths relative to repository root).
- Record concrete evidence, issues and handoff per `docs/HANDOFF.md`.
