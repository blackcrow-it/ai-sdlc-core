---
name: sdlc-domain-modeling
description: Build and sharpen the project's domain model while you design - challenge fuzzy or conflicting terms, stress-test them with edge-case scenarios, and update GLOSSARY.md and ADRs inline. Use when discussing domain terminology, writing or editing GLOSSARY.md, or recording or editing an architecture decision (ADR).
metadata:
  package: ai-sdlc-core
  version: "0.1.1"
---

Actively build the project's domain model as decisions are made. This is the _active_ discipline: challenging terms, inventing edge-case scenarios and writing the glossary and decisions down the moment they crystallise. Merely _reading_ `GLOSSARY.md` for vocabulary is a habit every SDLC role already has; this skill is for when the model changes.

## Where the documents live

Single context (almost every repository):

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

If `GLOSSARY-MAP.md` exists at the root, the repository has several contexts and the map points at one `GLOSSARY.md` (and optionally one `docs/adr/`) per context; root `docs/adr/` keeps system-wide decisions. Infer which context the topic belongs to; ask when unclear.

Create files **lazily**: `GLOSSARY.md` when the first term is resolved, `docs/adr/` when the first ADR is needed. Never create empty scaffolding. Inside an Orca worker, write these files only when they are inside the task's `allowed_paths`; otherwise propose the change in the handoff.

## During the session

- **Challenge against the glossary.** When a term conflicts with `GLOSSARY.md`, say so at once: "The glossary defines _cancellation_ as X, but you seem to mean Y. Which is it?"
- **Sharpen fuzzy language.** For a vague or overloaded word, propose one precise canonical term: "By _account_ do you mean the Customer or the User? Those are different things."
- **Discuss concrete scenarios.** Invent scenarios that probe the edges between concepts and force a precise answer.
- **Cross-reference with code.** When the user states how something works, check whether the code agrees and surface contradictions: "The code cancels whole Orders, but you said partial cancellation is possible. Which is right?"
- **Update `GLOSSARY.md` inline**, the moment a term is resolved, in the format of [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md). The glossary holds domain language only: no implementation details, specs or scratch notes.
- **Offer ADRs sparingly**, only when the decision is hard to reverse, surprising without context **and** the result of a real trade-off. Use [ADR-FORMAT.md](ADR-FORMAT.md).

## Consuming the model (every SDLC skill)

- Name domain concepts (task titles, acceptance criteria, test names, hypotheses, module names) with the glossary's terms, never with the synonyms it lists under _Avoid_.
- A concept the glossary lacks is a signal: either you are inventing language the project does not use, or there is a real gap to resolve with this skill.
- When your output contradicts an ADR, say so explicitly instead of silently overriding it: _"Contradicts ADR-0007 (event-sourced orders), but worth reopening because..."_.
