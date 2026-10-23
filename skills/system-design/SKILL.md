---
name: system-design
description: Design software architecture, APIs and databases with tradeoffs, ADRs, security boundaries, migration and rollback plans. Use for new systems and significant technical change.
---

# System Design

**When to use:** Design software architecture, APIs and databases with tradeoffs, ADRs, security boundaries, migration and rollback plans. Use for new systems and significant technical change.

## Inputs
Inputs: approved requirements, non-functional targets, codebase baseline.

## Procedure
1. Inspect the current codebase and record factual constraints.
2. Propose components, interfaces, data ownership, error handling and API contracts.
3. Compare alternatives, document decision rationale and security/trust boundaries.
4. Design tests, migration, observability and rollback considerations.

## Output
Produce architecture diagram (Mermaid when useful), ADRs, API/data spec and open risks.

## Safety and quality
- Never authorize significant design changes without the applicable approval.
- Apply `policies/permissions.md` and `policies/quality-gates.md` (paths relative to repository root).
- Record concrete evidence, issues and handoff per `docs/HANDOFF.md`.
