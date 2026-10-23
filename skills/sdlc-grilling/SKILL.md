---
name: sdlc-grilling
description: Interview the user through the available interactive question tool, exploring a plan, decision, brief, spec or task breakdown until each branch is decided or explicitly open. Use when the user wants to stress-test their thinking, says "grill me", or another SDLC skill needs human decisions.
metadata:
  package: ai-sdlc-core
  version: "0.1.3"
---

Interview the user until you reach a **shared understanding**. Map the work as a **design tree**: every decision
branches into the decisions that hang off it. Use the host's interactive question tool for the interview; Markdown
is for context and summaries, or a fallback when a question cannot be asked through an available, permitted tool.

## 1. Prepare the tree and choose the tool

Read the code, docs, `.ai-sdlc/project.json`, `GLOSSARY.md`, ADRs and relevant tracker records. Separate facts you
can verify from decisions the human owns. Reuse decisions already given in this session; ask again only when new
evidence creates a conflict, or a changed scope invalidates them. Ask in `project.reply_language` (default Vietnamese).

Before the first question, inspect the tools actually exposed in this session and their instructions. Choose an
available **and permitted** interactive question tool. Tool names, schemas, mode restrictions and limits come
from the host, not from this skill. Read [TOOL-INTERVIEW.md](TOOL-INTERVIEW.md) for host adapters, asynchronous
delivery, free-text limitations and fallback. A tool mentioned in this document is not automatically callable.

Keep a lightweight decision record in session context: stable question ID, question, prerequisites, recommendation,
state, actual answer and source. Use states `pending`, `answered`, `deferred` or `blocked`. Track owner and what a
deferred/blocked decision prevents. This is interview state, not a second task tracker; pass decided/open items to
the calling skill's artifacts. Do not create an extra persistent interview file unless the task asks for one.

## 2. Ask small interactive batches

The **frontier** contains decisions whose prerequisites are settled. Ask only questions from that frontier:

- Prefer one focused decision per question. Batch 1–3 independent questions, or fewer if the tool requires it;
  split a larger frontier into successive batches. Recompute after every reply, including between batches.
- Use a self-contained prompt, a short title/header and a stable ID where the tool supports one. Keep the ID in
  your decision record if the tool has no ID field. Include enough context and the trade-off to choose.
- For a choice, offer 2–3 realistic, mutually exclusive options when supported. Put the recommendation first,
  mark it as recommended in the tool's supported form, and explain why briefly. A default or preselection is
  merely a recommendation. Free text can override the offered choices.
- Ask for free text when the answer is a name, constraint, business rule or another value choices would distort.
  Use the host's free-text affordance; do not invent options just to satisfy a schema. Ask separate questions
  for independent choices; use multiple selection only when the actual tool supports it and choices can coexist.
- Ask directly about the decision rather than making a bare "yes" stand for several recommendations. Numbering
  is an internal aid, not a requirement to render a Markdown questionnaire beside the interactive controls.

Call the selected tool with its actual schema, then wait for the user's response. Ask questions dependent on an
unanswered choice only after that choice is resolved. Continue independent read-only exploration while an
asynchronous question is pending; do not do work that assumes an answer.

## 3. Process replies, then recompute

Map actual submitted answers to their question IDs. Record the user's words or a faithful interpretation and its
source, including replies sent as ordinary chat while a tool question is pending. Apply corrections to the decision
record and revisit affected descendants; keep unrelated answers. Clarify an ambiguous reply rather than guessing
which question it answers. Ask only the unresolved follow-up, not the whole completed batch.

Only submitted answers settle decisions. Tool completion, elapsed time, empty/partial results, dismissed UI,
preselected options and silence are not consent. Preserve pending questions when a response can still arrive.
If the user skips, says "later" or "not sure", record a deferred decision with owner (from `sdlc.approvers` when
appropriate) and what it blocks. Follow host rules for optional unanswered questions: mark them unresolved and
continue independent work without repeatedly prompting or treating the recommendation as accepted. Required
decisions remain blocking; ask through a permitted channel when the tool cannot carry them.

Finding facts remains your job. Look them up rather than asking the user; use a scoped research sub-agent when
needed and authorized. A pending lookup blocks only its dependent questions. Never invent numbers, legal duties,
approvals or integrations. Hand actual domain decisions to `sdlc-domain-modeling` when the calling workflow uses it.

## 4. Workers and permissions

Inside a supervised Orca worker, route decisions to the Orchestrator through the installed orchestration guide's
ask/reply flow. Do not open a separate user interview just because an interactive tool is exposed. If ask/reply is
unavailable, report the decisions, owner and blockers in the handoff. Never resolve them yourself.

Distinguish an interview answer from approval to publish, dispatch, change protected scope or release. Use the
approval channel required by the host and calling workflow. In particular, preserve `APPROVE-SDLC-PLAN` and
`START-ORCA-SMOKE-TEST` where required; a selected option or shared-understanding confirmation cannot replace them.

## 5. Close the interview

Finish when every reachable branch has been explored and every leaf is answered or explicitly open with an owner
and blocker. A question merely waiting for an answer is still pending. Summarise settled decisions and open items
separately, then request confirmation of that specific summary through the permitted interactive tool (or fallback
channel). If the host reserves a tool for optional clarification or prohibits approval requests, use ordinary chat
for a required confirmation. Reuse explicit confirmation already given for that same summary.

After actual confirmation, return the decision record and unresolved blockers to the calling workflow. It decides
which artifacts to write and what can proceed; dependent work stays blocked by required open decisions. Do not
start implementation, publish or dispatch merely because the interview is complete.
