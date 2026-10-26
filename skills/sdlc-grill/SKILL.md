---
name: sdlc-grill
description: A relentless interview that sharpens a plan, feature idea or change in this repository, and records resolved domain terms in GLOSSARY.md and hard-to-reverse decisions as ADRs as it goes.
argument-hint: "The plan, idea or change to sharpen"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.7"
---

Call the Skill tool twice, for "sdlc-grilling" and "sdlc-domain-modeling", then interview the user about the plan
through the grilling skill's permitted interactive question tool. Follow its batch limits, answer tracking and
fallback; keep summaries and domain decisions in this session.

Before the first round, read `.ai-sdlc/project.json` if it exists (reply language, `scope`, coding rules, approvers), `GLOSSARY.md` or `GLOSSARY-MAP.md`, the ADRs in `docs/adr/`, `docs/brief.md` and the code the plan touches. Challenge anything that falls outside `scope.in_scope` or inside `scope.out_of_scope`.

When the frontier is empty and the user confirms the shared understanding, recommend the next step without starting it:

- a multi-session build → `/sdlc-spec` in this same session, then `/sdlc-plan`;
- one small change → `/sdlc-task`, then `/sdlc-implement`;
- a whole product or a change that needs every SDLC phase → `/sdlc-brief` (if there is no brief), then `/sdlc-orchestrate`.

Keep this session's context until the spec or plan is written: the grilling is its primary source.

For a feature/change, read the project's documentation map and relevant canonical PRD/SRS/contract sections per
core `references/DOCUMENTATION-CONTINUITY.md`. Carry affected requirement IDs, baseline gaps and document impacts
into the conversation so the next spec/plan accounts for them; unresolved impacts keep an owner and blocker.
