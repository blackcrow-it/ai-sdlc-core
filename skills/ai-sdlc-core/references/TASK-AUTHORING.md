# Authoring task contracts

Shared rules for every skill that writes task contracts: /sdlc-task (one task), /sdlc-plan (a breakdown),
/sdlc-triage (an incoming issue made agent-ready) and the Orchestrator (a DAG for an objective). `SDLC` is
`python "<CORE>/scripts/sdlc.py"`; tracker operations follow `references/trackers/<tracker.provider>.md`.

A task contract is the **only** brief a worker gets. The worker explores the code fresh, possibly days later, so the
contract must stay true while files move: it states **what** must be true when the task is done, not **how** to edit.

For every new project or change, read `references/DOCUMENTATION-CONTINUITY.md` before slicing. Assess the canonical
documentation map and the spec's impact table; every affected artifact must have an owning update task, scope,
deliverable and acceptance criterion. Requirements updates precede dependent code; final evidence/document
reconciliation blocks feature acceptance. Do this for one-task fixes and triage too, not only full SDLC Runs.

## Slicing: tracer bullets

Break work into **tracer-bullet** tasks: vertical slices, not horizontal layers.

- Each slice cuts a narrow but **complete** path through every layer it needs (schema, API, UI, tests). "All the
  database tables" or "all the endpoints" is a horizontal slice; reject it.
- A finished slice is **demoable or verifiable on its own**: its acceptance criteria can be checked without waiting
  for a sibling.
- Each slice fits **one fresh context window** of one worker. Too big to state in a handful of acceptance criteria
  means too big: split it.
- **Prefactor first.** "Make the change easy, then make the easy change": a refactor that makes the feature simple is
  its own task (behaviour unchanged, `test_seams` at the new interface) and blocks the feature tasks.
- **Documents are slices too.** Requirements, design, architecture and test-plan tasks deliver documents at named
  paths with checkable acceptance criteria (sections present, every requirement traced to a test, open questions
  listed with owners).

**Wide refactors are the exception.** One mechanical change whose **blast radius** fans across the codebase (renaming
a column, retyping a shared symbol) cannot land green as one vertical slice. Sequence it **expand-contract**:

1. **Expand**: add the new form beside the old so nothing breaks.
2. **Migrate** the call sites in batches sized by blast radius (per package or directory), each its own task blocked
   by the expand, CI green after each batch because the old form still exists.
3. **Contract**: delete the old form once no caller remains, blocked by every migrate batch.

When even the batches cannot stay green alone, keep the sequence but let them share an integration branch, all
blocking a final integrate-and-verify task; green is promised only there.

## Blocking edges

`dependencies` lists the task IDs that must be `accepted` before this one can start, and only those: an edge that does
not genuinely gate the work serialises the plan for nothing. A task with no dependencies can start immediately.

The **frontier** is every task whose status is `ready` and whose dependencies are all `accepted`; workers (or
/sdlc-implement) take tasks from the frontier. A purely linear chain is worked top to bottom.

Run `SDLC validate --task <a> --task <b> ...` over the whole breakdown: it rejects duplicate IDs and dependency cycles
and warns about dependencies outside the set.

## Fields

| Field | Rule |
|---|---|
| `title` | Imperative, in the glossary's domain terms: "Reject expired coupons at checkout", not "Fix coupon bug" |
| `owner_agent` / `reviewer_agent` | Enabled roles, different from each other; reviewer per `references/ROLE-ASSIGNMENT.md` |
| `scope.allowed_paths` | The write ceiling: as narrow as the change allows, inside the project's `scope.allowed_paths`, outside protected paths. It bounds the worker; it is not a list of edit instructions |
| `acceptance_criteria` | Observable and independently checkable, Given/When/Then where it helps. "Login works" is not a criterion; "Given a locked account, when the user signs in with the right password, then sign-in is refused and the lock reason is shown" is |
| `test_seams` | **Required for implementation roles** (frontend, backend, devops). The public interfaces the tests exercise, highest first, fewest possible, existing seams preferred; one line each on what it catches. Vocabulary: the `sdlc-codebase-design` skill |
| `documentation` | Required for newly authored tasks: `assessment` plus owned `updates` (`path`, `change`, `requirement_ids`) per `references/DOCUMENTATION-CONTINUITY.md`. Empty updates need a justified no-impact decision or references to owning tasks; legacy omissions must be assessed before execution/acceptance |
| `required_checks` | The project's configured commands that must pass (lint, typecheck, test, e2e, security as applicable) |
| `deliverables` | What exists when done: source and tests, a document at a named path, a review report |
| `input_artifacts` | Pointers to the brief, spec, SRS, ADRs, prototype branch or source issue the work comes from. Point, do not paste |
| `dependencies` | See above |
| `risk_level`, `priority`, `max_attempts`, `human_approval_required` | `human_approval_required: true` for anything touching auth, payments, personal data, migrations or releases |

Wording rules:

- **Durable over precise.** Name types, interfaces, behaviours and config shapes; never line numbers. Paths belong in
  `allowed_paths` and `input_artifacts`, not in acceptance criteria.
- **Behavioural, not procedural.** "Expired coupons are rejected with reason `coupon_expired`", not "add an `if` in
  `applyCoupon`".
- **Explicit out of scope.** When an adjacent change is tempting, add a criterion such as "the coupon admin screen is
  unchanged" so the worker does not gold-plate.
- **Glossary terms only**, never the synonyms `GLOSSARY.md` lists under _Avoid_; respect the ADRs in the area.
- A snippet is allowed only when a prototype produced something that encodes a decision more precisely than prose
  (a state machine, a schema, a type shape); trim it to the decision and say it came from a prototype.

## Review with the user

Present the draft (one task or the breakdown) as a numbered list: title, owner → reviewer, blocked by, what it
delivers, test seams. Keep that draft as review context, then use the permitted interactive question tool and
small independent batches from the `sdlc-grilling` skill to ask:

- Does the granularity feel right (too coarse, too fine)?
- Does each dependency genuinely gate its task?
- Should any task be merged or split? Are the test seams the ones you expect?
- Does every affected canonical document have an owner, scope and verification? Are baseline updates and final
  traceability reconciliation correctly sequenced, including shared document writers?

Iterate until the user approves. Interview answers do not substitute for publication approval: use the channel
permitted by the host/calling workflow for that approval. Without approval nothing is published.

## Publish

1. Number tasks with the tracker's "Next ID" recipe.
2. Draft each contract with `SDLC task new --id TASK-NNN --title "<title>" --role <owner> [--reviewer <role>]`,
   replace every `REPLACE` placeholder with the agreed values, set `status` to `ready` for approved work (`draft`
   otherwise), and run `SDLC validate --task <file>` until it passes.
3. Run the graph check over the whole breakdown (`SDLC validate --task ... --task ...`).
4. Publish **in dependency order, blockers first**, so every dependency names a task that already exists. On a remote
   tracker this is outward-facing: confirm with the user before the first issue is created, then follow the tracker's
   "Create" and "Verify round-trip" recipes for each task. On the local tracker the files are the record; commit them
   with the message `Plan <feature>: TASK-NNN..TASK-MMM`.
5. Never close or edit a parent or source issue while publishing; link to it instead.
