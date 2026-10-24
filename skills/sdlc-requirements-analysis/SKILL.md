---
name: sdlc-requirements-analysis
description: Turn a brief, spec, stakeholder input or an existing SRS into traceable PRD/SRS documents, user stories and measurable acceptance criteria, with verified facts separated from assumptions and open questions routed to their owner. Use for discovery, requirements, UX specs, backlog grooming, release planning and documentation tasks.
metadata:
  package: ai-sdlc-core
  version: "0.1.5"
---

# Requirements analysis

Primary skill of the product, analysis, UX, planning and documentation roles. Inputs: the task contract or the user's request, the brief or spec it points at (`input_artifacts`), `.ai-sdlc/project.json` (`scope`, approvers) and the existing product.

Read the assigned `agents/<owner_agent>.md` and core `references/ROLE-PROFILE-CONTRACT.md` before choosing the
artifact. With no assigned role, infer the artifact from the request; clarify only material ambiguity. The role
specialises this procedure; sharing a skill does not make every task a requirements-writing task.

| Assignment | Primary artifact and focus |
|---|---|
| Product/discovery | Problem/evidence assessment, scope and outcome measures in the canonical brief/PRD |
| BA/requirements | Rules, use cases, functional/NFR changes and criteria in the canonical SRS/PRD |
| UX/UI | Journeys, interaction/component states, tokens and evaluation limits in `templates/UI-SPEC.md` or existing UI spec |
| Project planning | Tracker contracts and dependencies per core `references/TASK-AUTHORING.md`; no second task list |
| Technical writing | Audience-specific guide/reference/migration/release content verified against the named code/release revision |

Create or update only the assigned artifacts. A planning, UI or writing task may cite requirements without
authoring a new PRD/SRS. New product rules or missing required baselines go to their owner instead of being
silently filled in by the current role. Use the canonical documents and phase templates that fit the assignment.

## Procedure

1. **Read the sources** and the project's domain language: `GLOSSARY.md` (or `GLOSSARY-MAP.md`) and the ADRs in `docs/adr/`. Use glossary terms throughout; a needed concept the glossary lacks is a finding.
   Read core `references/DOCUMENTATION-CONTINUITY.md`, the documentation map and existing PRD/SRS baselines.
   Maintain canonical documents at their existing paths; feature specs link to them. For missing baselines,
   reconstruct verified behavior and label assumptions, gaps and pending approvals rather than inventing history.
2. **Separate verified facts from assumptions.** A fact cites its source (brief section, existing code path, stakeholder message). Everything else is an assumption, listed as such.
3. **Produce the assigned artifact** using the route above and the role profile's working method. For a requirements-authoring task, use the phase's PRD/SRS template and cover:
   - user roles and journeys; business rules; edge cases and error behaviour; constraints; non-functional targets with numbers only when a source gives them;
   - **user stories/use cases** that cover scoped actors and journeys, `As a <actor>, I want <capability>, so that <benefit>` where useful;
   - **acceptance criteria** that are observable and independently checkable, Given/When/Then where it helps.
4. **Trace the artifact.** Preserve existing requirement IDs and map changed requirements to source, criteria and later tests. Non-requirements artifacts link to the applicable requirements, contract, code or release revision; do not invent new business requirements or IDs merely to document a command or plan a task. Unrequested product behaviour needs a scope decision.
5. **Resolve ambiguity with the owner, never by guessing.** With the user in the session, call the Skill tool with "sdlc-grilling" and use its permitted interactive question tool, small batches and answer tracking. In an Orca worker, send the questions to the Orchestrator or list them as open questions with their owner (usually `product_owner`) and what they block. When a business rule only becomes clear by trying it, propose a prototype (the `sdlc-prototype` skill) instead of prose.
6. **Keep the domain model current.** When a term is resolved or an overloaded word is split, call the Skill tool with "sdlc-domain-modeling" and update `GLOSSARY.md`, if it is inside the task's `allowed_paths` (otherwise propose the entry in the handoff).
7. **Reconcile the baseline.** Update affected PRD/SRS sections, stable requirement IDs, the canonical coverage
   matrix and revision/review history within this task's scope. Keep superseded IDs with links and earlier
   approvals attached to their earlier revisions. For a final reconciliation task, inspect the integrated
   documents and linked task/test evidence; unresolved required updates block feature acceptance. Run
   `SDLC docs-check --task <contract> --base <recorded base>` (`SDLC` is the core `scripts/sdlc.py` entry point).

## Output

The assigned artifacts at canonical deliverable paths, with sources/traceability appropriate to their role,
verification evidence and unresolved decisions (question, owner, blocks). Requirements tasks include the
requirement → source → acceptance-criteria matrix. Hand off per core `references/HANDOFF.md`.

## Rules

- Never invent stakeholder approval, legal or compliance duties, numbers, integrations or domain rules.
- Stay inside `scope.in_scope`; anything in `scope.out_of_scope` or `.out-of-scope/` is flagged, not specified.
- Apply core `policies/permissions.md`, `policies/approval-rules.md` and `policies/quality-gates.md` of the `ai-sdlc-core` skill (locate it with `sdlc.py where`) and the project rules in `.ai-sdlc/project.json`.
