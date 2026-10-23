---
name: sdlc-help
description: Ask which AI SDLC skill or flow fits your situation - a map of every skill in the package, the flows that connect them, and when to clear or compact the context.
argument-hint: "Your situation, e.g. \"I have an SRS in Word\" or \"tests are flaky\""
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.4"
---

# AI SDLC help

Answer the user's question with the flow that fits, in the project's reply language. Before stating what a skill does or recommending that a step be skipped, read that skill's `SKILL.md` (siblings of this skill's directory): the summaries below are for orientation only. If the repository has a config, run `python "<CORE>/scripts/sdlc.py" doctor --offline` (`<CORE>` is the sibling `ai-sdlc-core` directory) so the answer starts from the real state.

A **flow** is a path through the skills. There is one precondition, two main flows, a few on-ramps that merge onto them, a loop-closer, and a vocabulary layer underneath that the other skills pull in.

## Precondition

**`/sdlc-setup`** once per repository: detects the stack, interviews you, writes `.ai-sdlc/project.json` (commands, coding rules, scope, approvers and the one **tracker** where task contracts live). **`/sdlc-status`** at any time tells you what is ready and which command comes next.

## Main flow A: a product or a change that needs every SDLC phase

For a new product, or work that needs requirements, UX, architecture, development, testing and release with human gates and parallel Orca workers.

1. **`/sdlc-brief`** interviews you and writes `docs/brief.md` (skip it when you already have a brief, PRD or SRS: convert Word or PDF documents to Markdown in the repository first and point at that file).
2. **`/sdlc-setup`** if the repository has no config yet.
3. **`/sdlc-smoke`** once, to prove Orca orchestration works end to end in this environment.
4. **`/sdlc-orchestrate docs/brief.md`** makes this session the Orchestrator: it plans a task DAG across the enabled phases, **stops for `APPROVE-SDLC-PLAN`**, then dispatches supervised workers in separate worktrees, verifies every result against real artifacts and checks, and keeps the tracker current.

## Main flow B: a feature or change in an existing project

The route most day-to-day work travels.

1. **`/sdlc-grill`** sharpens the idea by interview and records resolved terms in `GLOSSARY.md` and hard-to-reverse decisions as ADRs. Start here whenever the idea is not yet crisp.
2. **Detour when a question needs a runnable answer** (a state model, a business rule, a screen you need to see): **`/sdlc-prototype`** builds throwaway code that answers it. When the answer needs external facts, **`/sdlc-research`** reads primary sources in the background and leaves a cited note.
3. **Is it a multi-session build?**
   - **Yes** → **`/sdlc-spec`** (turn the conversation into `docs/specs/<feature>.md`), then **`/sdlc-plan`** (tracer-bullet task contracts with blocking edges, published to the tracker). Then build them one of two ways:
     - **`/sdlc-implement <task>`** per task in this repository, **clearing the context between tasks**, taking tasks from the frontier (ready, every dependency accepted);
     - **`/sdlc-orchestrate`** to let Orca workers build the frontier in parallel worktrees under your approval.
   - **No, one small change** → **`/sdlc-task`** (one validated contract), then **`/sdlc-implement`**.

Either way the code is built test-first at the contract's test seams (`/sdlc-tdd`, driven by `/sdlc-implementation`) and checked by an independent `/sdlc-code-review` on three separate axes (spec, standards, risk) before a human accepts it.

## On-ramps

- **Bugs and requests piling up on GitHub, GitLab or Jira** → **`/sdlc-triage`**. It categorises, verifies, grills when needed and turns agent-ready issues into task contracts that `/sdlc-implement` or `/sdlc-orchestrate` pick up. Only for issues you did not write: tasks from `/sdlc-plan` are already agent-ready.
- **Something is broken** → **`/sdlc-debugging`**. For the hard ones: the bug that resists a first look, the flaky test, the regression between two known-good states. It refuses to theorise until it has a red-capable feedback loop, then fixes with a regression test. When the fix needs a tracked change, write it as a task (`/sdlc-task`).
- **An existing SRS or PRD** → convert it to Markdown in the repository, then `/sdlc-plan <file>` for a feature-sized document or `/sdlc-orchestrate <file>` when it still needs design and architecture phases.

## Closing the loop

**`/sdlc-retro`** after a session, task or Run, especially one that went sideways. It proposes changes to the **environment**, not the code: navigation pointers, automated checks, coding rules, task-authoring rules, steering files, tooling. Mechanical mistakes become deterministic checks; judgement calls become coding rules for review. Run it in the session it looks back on, before you clear.

## Vocabulary underneath

Model-invoked references that the skills above (and Orca workers) load on their own. Reach for them directly when the words, not the process, are the problem.

- **`/sdlc-grilling`**: the interactive interview primitive behind `/sdlc-grill`, `/sdlc-brief`, `/sdlc-setup`,
  `/sdlc-task`, `/sdlc-plan` and `/sdlc-triage`: use a permitted question tool, small independent batches and actual
  submitted answers. It tracks pending/deferred decisions, handles async replies and falls back to chat only when
  needed. Worker questions still go to the Orchestrator; approval rules stay with the calling workflow.
- **`/sdlc-domain-modeling`**: sharpen the domain language and keep `GLOSSARY.md` and `docs/adr/` current.
- **`/sdlc-codebase-design`**: the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) for the shape of a module and the choice of test seams.
- **`/sdlc-tdd`**: the red-green loop and what makes a test worth keeping.

## Role skills (what Orca workers run)

Each role in `agents/registry.json` has a primary skill; `/sdlc-implement` and Orca workers load it for the task's owner and reviewer: **`/sdlc-requirements-analysis`** (product, analysis, UX, planning, documentation), **`/sdlc-system-design`** (architecture, data), **`/sdlc-implementation`** (frontend, backend, DevOps), **`/sdlc-code-review`** (review) and **`/sdlc-testing`** (QA, security).

## Where things live

Both main flows maintain the canonical project documents under core `references/DOCUMENTATION-CONTINUITY.md`.
Setup inventories applicable artifacts; spec assesses impact on existing PRD/SRS, design, contracts, tests and guides;
planning assigns updates and dependencies; task owners run `docs-check`; independent review and final integrated
reconciliation verify semantic consistency and requirement-to-evidence links before feature acceptance. Feature
specs supplement the product baseline. Legacy projects/tasks must assess missing documents instead of assuming
that creating a new feature spec updates their SRS automatically.

| What | Where |
|---|---|
| Project config | `.ai-sdlc/project.json` (only via `/sdlc-setup` or with approval in `/sdlc-retro`) |
| Canonical document index / gaps | `docs/documentation-map.md` or the project's existing equivalent |
| Brief, specs, research | `docs/brief.md`, `docs/specs/`, `docs/research/` (committed) |
| Domain language and decisions | `GLOSSARY.md` (or `GLOSSARY-MAP.md`), `docs/adr/` |
| Task contracts | Only the tracker chosen in setup: `.ai-sdlc/tasks/` (local) or one issue per task |
| Rejected enhancement requests | `.out-of-scope/` |
| Generated prompts, specs and drafts | `.ai-sdlc/runs/` (ignored by Git) |

## Phase boundaries

A **phase** is a chunk of work inside a session (the grilling, the spec, one task). At the boundary between two phases you choose between **continue**, **`/clear`**, a **handoff**, a **sub-agent** and **`/compact`**. Decide at the boundary, never mid-phase. Keep grill → spec → plan in **one unbroken context**: the plan wants the grilling verbatim, not a summary. Each `/sdlc-implement` then starts fresh from its task contract. Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered decision tree.
