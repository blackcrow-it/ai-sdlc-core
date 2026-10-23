---
name: sdlc-requirements-analysis
description: Analyze feature and business requirements into traceable PRD/SRS, user stories and measurable acceptance criteria. Use for discovery, requirement clarification, backlog grooming and documentation.
metadata:
  package: ai-sdlc-core
  version: "2.1.0"
---

# Requirements Analysis

**When to use:** Analyze feature and business requirements into traceable PRD/SRS, user stories and measurable acceptance criteria. Use for discovery, requirement clarification, backlog grooming and documentation.

## Inputs
Inputs: stakeholder brief, project constraints, existing features and user roles.

## Procedure
1. Read stakeholder brief and identify verified facts vs assumptions.
2. Write user journeys, rules, edge cases, roles, constraints and non-functional targets.
3. Produce acceptance criteria using Given/When/Then or another unambiguous form.
4. Map each requirement to an artifact/test ID; ask for human resolution of ambiguous rules.

## Output
Deliver PRD/SRS or task-ready stories, open questions and a coverage matrix.

## Safety and quality
- Never invent stakeholder approval or domain/legal rules.
- Apply core `policies/permissions.md` and `policies/quality-gates.md` from the `ai-sdlc-core` skill (locate with `sdlc.py where`), plus project rules in `.ai-sdlc/project.json` (commands, coding rules, protected paths).
- Record concrete evidence, issues and handoff per core `references/HANDOFF.md`.
