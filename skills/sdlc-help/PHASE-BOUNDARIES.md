# Phase boundaries

A **phase** is a chunk of work inside a session: the grilling, the spec, the plan, one task's implementation, a
review. The definition is fuzzy on purpose: a phase ends when you think "done with that". The **boundary** between two
phases is the only place to decide what happens to the context. Mid-phase there is nothing to decide: continue, or
split the remaining work into sub-agents. Compacting mid-phase makes the agent lose the thread.

## The five options

| Option | What it does |
|---|---|
| **Continue** | Stay in the session; no context switch |
| **`/clear`** | Empty the context window and start from nothing |
| **Handoff** | Write a portable file (or use Orca's worktree handoff) and seed a session elsewhere |
| **Sub-agent** | Send a tightly scoped task to its own context and get a report back |
| **`/compact`** | Compress this context and continue from the summary |

## The tree

Work top to bottom at the boundary; the first **yes** wins.

**1. Can you continue here?** Yes when the next phase needs this one as a **primary source** (grill → spec → plan:
the plan wants the reasoning verbatim), or when enough of the window remains for the next phase. Continue costs
nothing and loses nothing, so rule it out first.

**2. Is this context irrelevant to what comes next?** Then **`/clear`**: cheapest move, whole window back, and the old
session stays resumable. Between two `/sdlc-implement` tasks this is the standard answer: each task contract is
self-contained. The cost of getting it wrong is one-way: clear a relevant context and the **why** behind the work is
gone; no diff gives it back.

**3. Does the work have to travel?** A handoff is narrow: a **new harness** (Claude Code → Codex), a **new directory
or worktree**, a **colleague**, or a side task found **mid-phase** that you fork without derailing the current one. In
Orca, a full ownership transfer to another worktree uses the `orca-cli` handoff. If nothing travels, you do not need
one.

**4. Can it run without you?** Tightly scoped work that needs no steering goes to a **sub-agent** (or, for SDLC tasks,
a supervised Orca worker) and leaves this session untouched. Independent review is the standard case: the reviewer
reads the diff and the task contract and reports.

**5. Otherwise, `/compact`.** Relevant context, same harness, same directory, you need to stay in the loop. Give it an
instruction (`/compact keep the decisions on TASK-004 test seams`) so the summary keeps what the next phase needs.

`/compact` is the default, not the first reach: the four questions above are cheaper or more precise. Starting here
produces a fresh session that is confidently wrong about a decision the summary flattened.

## Primary and secondary sources

Every option except **continue** turns a **primary source** (the session as it happened) into a **secondary source**
(a summary of it): less noise and more room, but lossy. Pay that loss only when staying costs more than it saves. The
durable artifacts of this package (brief, spec, task contracts, ADRs, glossary, handoff reports) exist so that the
secondary source is written deliberately, not by a summariser.
