---
name: sdlc-grilling
description: Interview the user relentlessly about a plan, decision, brief, spec or task breakdown until every branch of the design tree is resolved. Use when the user wants to stress-test their thinking, says "grill me", or another SDLC skill needs decisions from the human before writing anything.
metadata:
  package: ai-sdlc-core
  version: "0.1.1"
---

Interview the user until you reach a **shared understanding**. Map the work as a **design tree**: every decision branches into the decisions that hang off it.

## Rounds

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you have not heard yet. Ask the whole frontier in one round, number each question and give your recommended answer. Then wait for the answers before the next round.

```
❓ **Q1 - <question title>**: <question body; may be several paragraphs, may list choices>

➡️ Recommended: <your answer and the one-line reason>

---

❓ **Q2 - <question title>**: ...
```

Word each question so "yes" accepts your recommendation. Ask in the project's reply language (`project.reply_language` in `.ai-sdlc/project.json`, default Vietnamese).

Each round reshapes the tree: settled decisions push the frontier outward and unblock the questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round.

## Facts are yours, decisions are theirs

Finding **facts** is your job: read the code, the docs, `.ai-sdlc/project.json`, `GLOSSARY.md`, `docs/adr/`, the tracker, `--help` output. Never ask the user for anything you can look up. When a fact needs real legwork, dispatch a sub-agent and keep asking the questions that do not depend on it; only the questions downstream of a running lookup wait for it.

**Decisions** belong to the user: put each one to them and wait. Never answer your own question, never record a recommendation as if the user had accepted it, and never invent numbers, legal duties, approvals or integrations.

When the user says "later" or "not sure", record an **open decision** with its owner (from `sdlc.approvers` when one fits) and what it blocks, and move on.

## No human in the loop

Inside an Orca worker there is no user to grill. Send the open decisions to the Orchestrator with the ask/reply flow of the installed orchestration guide, or stop and report them as blockers in the handoff. Never resolve them yourself.

## Done

The session is done when the frontier is empty: every branch visited, every leaf either decided or recorded as an open decision, nothing silently assumed. Summarise the decisions in one list, then ask the user to confirm the shared understanding. Do not act on it before they confirm.
