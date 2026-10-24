---
name: sdlc-testing
description: Plan and execute unit, integration, E2E, regression and security tests tied to acceptance criteria, judge test quality, reproduce defects with a red-capable loop, and give an evidence-based go/no-go. Use for QA, security testing, test reports and release validation.
metadata:
  package: ai-sdlc-core
  version: "0.1.5"
---

# Testing

Primary skill of the QA Engineer and Security Engineer. Inputs: acceptance criteria and requirement IDs, the code revision, `test_seams` of the tasks under test, the test environment and `.ai-sdlc/project.json` `commands`.

Read the assigned role profile and core `references/ROLE-PROFILE-CONTRACT.md`. QA emphasises risk-based journey
coverage and evidence limits; security adds threat/control/test mapping, assessment authorisation and findings
with exploitability/business impact. Use screenshots for visual state and assertions or recorded outcomes for
behaviour; missing evidence is not a fabricated defect. Apply project targets rather than upstream metric quotas.

## Procedure

1. **Map the criteria.** For every acceptance criterion and requirement in scope, list the test cases: happy path, edges, errors, authorisation and abuse cases, and the non-functional targets that have numbers. Each case names the requirement it covers.
2. **Choose the level and the seam.** Test behaviour through public interfaces at the agreed seams (unit, integration, E2E); reuse the project's existing test style. Call the Skill tool with "sdlc-tdd" for what makes a test worth keeping; flag existing tests that are implementation-coupled or tautological instead of trusting them.
3. **Use stable data.** Deterministic fixtures, pinned time and seeds, no production data, no real credentials.
4. **Run what is configured.** Use `commands.test`, `commands.e2e` and `commands.security` exactly as written; record environment, command, exit code and log path for each run.
5. **Reproduce every defect.** For a failure whose cause is not obvious, call the Skill tool with "sdlc-debugging" and stop after its Phase 2: a red-capable command and a minimised repro are the defect report. File it with the steps, the expected and actual result, the command that goes red and the requirement it violates. Fixing it is a separate task.
6. **Separate the outcomes.** `pass` only with a real run; `fail` with the repro; `blocked` with the missing prerequisite; `not_run` with the reason. Skipped and unavailable tests are listed distinctly, never folded into a pass.
7. **Verify documentation continuity.** Read core `references/DOCUMENTATION-CONTINUITY.md` and compare the
   documentation map/impact assessment with the integrated behavior. Update owned test plans and the canonical
   requirement → criterion → task → test → actual evidence matrix; confirm references and revisions exist.
   Report missing scope or stale documents to their owner. Run `SDLC docs-check --task <contract> --base <base>`
   (`SDLC` is core `scripts/sdlc.py`); its structural pass cannot replace semantic review or human baseline approval.

## Output

A test report from `templates/test-report.md`: coverage matrix (requirement → test cases → result), defects with repro commands, residual risks and a risk-based go/no-go recommendation. Hand off per core `references/HANDOFF.md`.

## Rules

- Never replace missing evidence with a speculative pass; never test against production unless a human explicitly approved that environment.
- Security testing stays inside the authorised scope and environments; no destructive or denial-of-service testing.
- Apply core `policies/permissions.md`, `policies/approval-rules.md` and `policies/quality-gates.md` of the `ai-sdlc-core` skill (locate it with `sdlc.py where`) and the project rules in `.ai-sdlc/project.json`.
