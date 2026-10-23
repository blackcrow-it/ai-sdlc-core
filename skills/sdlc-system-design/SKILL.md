---
name: sdlc-system-design
description: Design software architecture, module interfaces, APIs and data models as deep modules at clean seams, compare real alternatives, record hard-to-reverse decisions as ADRs, and plan security boundaries, test seams, migration and rollback. Use for new systems, significant technical change, database design and architecture reviews.
metadata:
  package: ai-sdlc-core
  version: "0.1.2"
---

# System design

Primary skill of the Software Architect and Database Engineer. Inputs: approved requirements (`input_artifacts`), non-functional targets, `.ai-sdlc/project.json` (`architecture`, `stack`, `scope`) and the codebase.

Call the Skill tool with "sdlc-codebase-design" first: use its vocabulary (module, interface, depth, seam, adapter, leverage, locality) exactly in every design.

## Procedure

1. **Record the factual baseline.** Inspect the code, configs and existing docs; note constraints with their evidence. Read `GLOSSARY.md` and the ADRs in `docs/adr/`; do not re-litigate an ADR without saying so explicitly.
2. **Shape the modules.** Propose modules, their interfaces (signatures plus invariants, ordering, error modes, configuration, performance), data ownership and integration between contexts. Aim for deep modules behind small interfaces; apply the deletion test to anything that looks like a pass-through. Classify each dependency (in-process, local-substitutable, remote but owned, true external) and choose the adapter strategy accordingly.
3. **Design it twice** for every significant interface or public API: produce radically different alternatives (the "Design it twice" reference of `sdlc-codebase-design`), compare them by depth, locality and seam placement, and recommend one.
4. **Draw the trust boundaries.** Authentication, authorisation, input validation, secrets handling, personal data, multi-tenant isolation; name the controls at each boundary.
5. **Choose the test seams.** For each module, the public interface its tests will exercise, highest first and as few as possible. These become the `test_seams` of the implementation tasks.
6. **Plan change safely.** Schema migrations (expand-contract for anything with a wide blast radius), backwards compatibility, observability (logs, metrics, traces at the seams), rollout and rollback. Destructive migrations are forbidden without human approval.
7. **Record decisions.** Call the Skill tool with "sdlc-domain-modeling" and write an ADR for each decision that is hard to reverse, surprising without context and the result of a real trade-off. ADRs that need the `tech_lead` stay `proposed` until that person accepts them.
8. **Update canonical design documents.** Follow core `references/DOCUMENTATION-CONTINUITY.md` and the contract's
   `documentation`: update owned architecture diagrams, API/data contracts, migration/rollback guidance and
   requirement references at their canonical paths. Preserve prior decisions with superseding links. Report
   out-of-scope impacts; run `SDLC docs-check --task <contract> --base <recorded base>` (`SDLC` is core `scripts/sdlc.py`).

## Output

The architecture document from `templates/architecture.md` (Mermaid diagrams where a graph communicates better than prose), API and data specifications, ADRs, the test-seam list per module and an open-risks table. Hand off per core `references/HANDOFF.md`.

## Rules

- Never approve your own significant design change; the approval rules decide who accepts it.
- Prefer existing seams and patterns; a new framework, datastore or service needs an ADR and approval.
- Apply core `policies/permissions.md`, `policies/approval-rules.md` and `policies/quality-gates.md` of the `ai-sdlc-core` skill (locate it with `sdlc.py where`) and the project rules in `.ai-sdlc/project.json`.
